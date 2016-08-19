#!/bin/env python
# -*- coding: utf-8 -*-
#
# Python implementation of Cardinal Splines
# Copyleft Juancarlo Añez <apalala@gmail.com>
#
# This code first published in https://gist.github.com/3308808
#
# References:
#    http://en.wikipedia.org/wiki/Cubic_Hermite_spline
#    http://www.codeproject.com/Articles/13864/Text-on-Path-with-VB-NET
#    http://www.planetclegg.com/projects/WarpingTextToSplines.html
#    http://stackoverflow.com/questions/7223283/php-interpolate-points-on-cardinal-curve
#

from __future__ import print_function, division
from collections import namedtuple

Point = namedtuple('Point', 'x y')

def addpt(a, b):
    x, y = zip(a, b)
    return Point(sum(x), sum(y))

def tangents(points, tension=0.5):
    def tangent(p0, p1, alf):
        return Point(alf * (p1.x - p0.x), alf * (p1.y - p0.y))

    if len(points) == 0:
        pass
    elif len(points) == 1:
        yield points[0]
    else:
        p = points
        yield tangent(p[0], p[1], tension)
        for i in xrange(1, len(p) - 1):
            yield tangent(p[i - 1], p[i + 1], tension)
        yield tangent(p[-2], p[-1], tension)

def interpolate(t, p0, m0, p1, m1):
    h00 = lambda t: (1 + 2 * t) * (1 - t) ** 2
    h10 = lambda t: t * (1 - t) ** 2
    h01 = lambda t: t ** 2 * (3 - 2 * t)
    h11 = lambda t: t ** 2 * (t - 1)

    h = [f(t) for f in (h00, h10, h01, h11)]
    xs, ys = zip(p0, m0, p1, m1)
    x = sum(f * v for f, v in zip(h, xs))
    y = sum(f * v for f, v in zip(h, ys))
    return Point(x, y)

def get_points(p0, m0, p1, m1):
    def intp(t):
        r = interpolate(t, p0, m0, p1, m1)
        return Point(int(r.x), int(r.y))

    domain = max(abs(p0.x - p1.x), abs(p0.y - p1.y))
    delta = 1 / domain

    last = intp(0)
    yield last

    t = delta
    while t < 1:
        p = intp(t)
        if p != last:
            yield p
            last = p
        t += delta

def cspline(points, tension=0.5):
    if len(points) < 2:
        for v in points:
            yield v
    else:
        m = list(tangents(points, tension))
        p = points
        for i in xrange(len(p) - 1):
            for v in get_points(p[i], m[i], p[i + 1], m[i + 1]):
                yield v
        yield p[-1]

if __name__ == '__main__':
    from random import seed, randint
    import turtle
    import sys

    def randpt():
        def randi(): return randint(-200, 200)
        return Point(randi(), randi())

    NPOINTS = 10

    seed(5)
    points = []
    for i in xrange(NPOINTS):
        points.append(randpt())
    cpoints = cspline(points, 0.7)

    turtle.hideturtle()

    turtle.penup()
    turtle.goto(points[0])
    turtle.pencolor('red')
    turtle.pensize(4)
    turtle.pendown()
    for p in points[1:]:
        turtle.goto(p)

    turtle.penup()
    turtle.goto(cpoints.next())
    turtle.pencolor('blue')
    turtle.pensize(2)
    turtle.pendown()
    i = 0
    for p in cpoints:
        i+=1
        turtle.goto(p)
    print(cpoints[34])

    turtle.mainloop()
