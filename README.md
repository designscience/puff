# puff
A Raspberry Pi program that accepts commands via TCP/IP and turns fire cannon channels on and off using GPIO output.

Since this is intended for flame effects, a watchdog timer protects channels from being on for more than a preset time.

The commands received follow this general format:
$command:version|param1:param1:etc#

Channel Execute - turn a single channel on or off
$chx:1|channel:on/off#
ex: $chx:1|18:1#

Bank Execute - sets all channels
$bnx:1|numChannels:on/off:on/off:etc#
ex: $bnx:1|18:0:0:1:0:0:1:0:0:1:0:0:1:0:0:1:0:0:1#

Kill - kill all channels
$kil:1|#
