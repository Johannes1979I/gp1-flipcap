#!/usr/bin/env python3
"""Carica un .hex su un Arduino Nano (optiboot, STK500v1) senza avrdude."""
import os, sys, time, termios, select, fcntl, struct
port, hexfile = sys.argv[1], sys.argv[2]
mem = {}
base = 0
for line in open(hexfile):
    line = line.strip()
    if not line.startswith(":"): continue
    b = bytes.fromhex(line[1:])
    n, addr, typ, data = b[0], (b[1] << 8) | b[2], b[3], b[4:4 + b[0]]
    if (sum(b) & 0xFF) != 0: sys.exit("checksum hex errato")
    if typ == 0:
        for i, v in enumerate(data): mem[base + addr + i] = v
    elif typ == 2: base = ((data[0] << 8) | data[1]) << 4
    elif typ == 4: base = ((data[0] << 8) | data[1]) << 16
size = max(mem) + 1
img = bytes(mem.get(i, 0xFF) for i in range((size + 127) // 128 * 128))
fd = os.open(port, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
a = termios.tcgetattr(fd)
a[0] = 0; a[1] = 0; a[2] = termios.CS8 | termios.CREAD | termios.CLOCAL; a[3] = 0
a[4] = a[5] = termios.B115200
a[6][termios.VMIN] = 0; a[6][termios.VTIME] = 0
termios.tcsetattr(fd, termios.TCSANOW, a)
TIOCMBIS, TIOCMBIC, DTR_RTS = 0x5416, 0x5417, 0x002 | 0x004
fcntl.ioctl(fd, TIOCMBIC, struct.pack("I", DTR_RTS)); time.sleep(0.1)   # reset: DTR giu'
fcntl.ioctl(fd, TIOCMBIS, struct.pack("I", DTR_RTS)); time.sleep(0.25)  # e su
termios.tcflush(fd, termios.TCIOFLUSH)
def rd(n, tmo=1.0):
    buf = b""; t = time.time()
    while len(buf) < n and time.time() - t < tmo:
        r, _, _ = select.select([fd], [], [], 0.05)
        if r: buf += os.read(fd, n - len(buf))
    return buf
def cmd(payload, nresp=0, tmo=1.0):
    os.write(fd, payload)
    r = rd(2 + nresp, tmo)
    if len(r) != 2 + nresp or r[0] != 0x14 or r[-1] != 0x10:
        raise IOError("risposta inattesa %r a %r" % (r, payload[:3]))
    return r[1:-1]
for i in range(20):
    try:
        cmd(b"\x30\x20", tmo=0.3); break
    except IOError:
        termios.tcflush(fd, termios.TCIFLUSH)
else:
    sys.exit("bootloader non risponde")
sig = cmd(b"\x75\x20", 3)
print("firma", sig.hex(), "| immagine", size, "byte,", len(img) // 128, "pagine", flush=True)
if sig != b"\x1e\x95\x0f": sys.exit("non e' un ATmega328P, mi fermo")
for off in range(0, len(img), 128):
    w = off // 2
    cmd(bytes([0x55, w & 0xFF, w >> 8, 0x20]))
    cmd(b"\x64\x00\x80\x46" + img[off:off + 128] + b"\x20", tmo=2.0)
for off in range(0, len(img), 128):
    w = off // 2
    cmd(bytes([0x55, w & 0xFF, w >> 8, 0x20]))
    got = cmd(b"\x74\x00\x80\x46\x20", 128)
    if got != img[off:off + 128]: sys.exit("VERIFICA FALLITA alla pagina %d" % (off // 128))
cmd(b"\x51\x20")
print("scritto e verificato:", size, "byte")
os.close(fd)
