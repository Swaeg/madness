#!/usr/bin/env python

spacing = 0.15  # m
lines = []
for c in range(-4, 4):
    rs = [range(60), reversed(range(60))][c % 2]
    for r in rs:
        lines.append('  {"point": [%.2f, %.2f, %.2f]}' %
                     (c*spacing, 0, (r - 24.5)*spacing))
print '[\n' + ',\n'.join(lines) + '\n]'
print len(lines)
