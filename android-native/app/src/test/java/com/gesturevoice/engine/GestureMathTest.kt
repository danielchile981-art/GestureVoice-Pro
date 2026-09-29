package com.gesturevoice.engine

import org.junit.Assert.*
import org.junit.Test

class GestureMathTest {
    @Test fun sameStrokeIsIdentical() {
        val a = listOf(Point(0f,0f,0), Point(.5f,.5f,100), Point(1f,1f,200))
        assertEquals(1f, GestureMath.similarity(a, a), .0001f)
    }
    @Test fun translationAndScaleDoNotChangeShape() {
        val a = listOf(Point(0f,0f,0), Point(.5f,1f,100), Point(1f,0f,200))
        val b = a.map { it.copy(x = it.x * .4f + .2f, y = it.y * .4f + .3f) }
        assertTrue(GestureMath.similarity(a, b) > .99f)
    }
    @Test fun oppositeDirectionDiffers() {
        val a = listOf(Point(0f,0f,0), Point(.5f,.5f,100), Point(1f,1f,200))
        assertTrue(GestureMath.similarity(a, a.reversed()) < .85f)
    }
    @Test fun clampCoordinates() {
        assertEquals(Point(0f,1f,0), GestureMath.clamp(listOf(Point(-1f,2f,-2))).first())
    }
}
