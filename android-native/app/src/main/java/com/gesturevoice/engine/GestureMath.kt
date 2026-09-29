package com.gesturevoice.engine

import kotlin.math.*

data class Point(val x: Float, val y: Float, val t: Long)

/** Reamostra um traço e preserva o tempo para reprodução em outra resolução. */
object GestureMath {
    fun clamp(points: List<Point>): List<Point> = points.map { Point(it.x.coerceIn(0f, 1f), it.y.coerceIn(0f, 1f), it.t.coerceAtLeast(0)) }
    fun smooth(points: List<Point>, factor: Float = .42f): List<Point> {
        if (points.isEmpty()) return points
        val result = mutableListOf(points.first())
        points.drop(1).forEach { p ->
            val last = result.last()
            result += Point(last.x + (p.x - last.x) * factor, last.y + (p.y - last.y) * factor, p.t)
        }
        return result
    }
    private fun distance(a: Point, b: Point): Float = hypot(a.x - b.x, a.y - b.y)
    fun resample(input: List<Point>, count: Int = 64): List<Point> {
        require(count >= 2)
        if (input.isEmpty()) return emptyList()
        if (input.size == 1) return List(count) { input.first() }
        val segments = input.zipWithNext { a, b -> distance(a, b) }
        val total = segments.sum()
        if (total < 1e-6f) return List(count) { input.first() }
        val cumulative = mutableListOf(0f)
        segments.forEach { cumulative += cumulative.last() + it }
        return (0 until count).map { i ->
            val target = total * i / (count - 1)
            val idx = (0 until segments.size).firstOrNull { cumulative[it + 1] >= target } ?: segments.lastIndex
            val a = input[idx]; val b = input[idx + 1]
            val ratio = ((target - cumulative[idx]) / segments[idx].coerceAtLeast(1e-6f)).coerceIn(0f, 1f)
            Point(a.x + (b.x - a.x) * ratio, a.y + (b.y - a.y) * ratio, (a.t + (b.t - a.t) * ratio).toLong())
        }
    }
    /** Forma independente de posição e escala para comparação $1; execução usa coordenadas originais. */
    fun shape(input: List<Point>): List<Point> {
        val sampled = resample(input)
        if (sampled.isEmpty()) return emptyList()
        val minX = sampled.minOf { it.x }; val maxX = sampled.maxOf { it.x }
        val minY = sampled.minOf { it.y }; val maxY = sampled.maxOf { it.y }
        val scale = max(maxX - minX, maxY - minY).coerceAtLeast(1e-6f)
        val centered = sampled.map { Point((it.x - minX) / scale, (it.y - minY) / scale, it.t) }
        val cx = centered.map { it.x }.average().toFloat(); val cy = centered.map { it.y }.average().toFloat()
        return centered.map { Point(it.x - cx, it.y - cy, it.t) }
    }
    fun similarity(a: List<Point>, b: List<Point>): Float {
        if (a.size < 2 || b.size < 2) return 0f
        val x = shape(a); val y = shape(b)
        val mean = x.indices.sumOf { i -> distance(x[i], y[i]).toDouble() }.toFloat() / x.size
        return (1f - mean / sqrt(2f)).coerceIn(0f, 1f)
    }
}
