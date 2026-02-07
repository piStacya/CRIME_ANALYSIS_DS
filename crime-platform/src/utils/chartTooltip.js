import { Interaction, Chart } from 'chart.js'

Chart.register({
  id: 'cssZoomFix',
  beforeEvent(chart, args) {
    const canvas = chart.canvas
    const rect = canvas.getBoundingClientRect()

    const zoomX = rect.width / canvas.clientWidth
    const zoomY = rect.height / canvas.clientHeight

    if (Math.abs(zoomX - 1) < 0.001 && Math.abs(zoomY - 1) < 0.001) return

    const e = args.event
    e.x = e.x / zoomX
    e.y = e.y / zoomY

    const ca = chart.chartArea
    if (ca) {
      args.inChartArea = e.x >= ca.left - 0.5 && e.x <= ca.right + 0.5 &&
                          e.y >= ca.top - 0.5 && e.y <= ca.bottom + 0.5
    }
  }
})

function isMouseOverAnyCanvas(x, y) {
  const canvases = document.querySelectorAll('canvas')
  for (const canvas of canvases) {
    const rect = canvas.getBoundingClientRect()
    if (x >= rect.left && x <= rect.right && y >= rect.top && y <= rect.bottom) {
      return true
    }
  }
  return false
}

document.addEventListener('mousemove', (e) => {
  if (!isMouseOverAnyCanvas(e.clientX, e.clientY)) {
    const el = document.getElementById('chartjs-tooltip')
    if (el) el.style.opacity = '0'
  }
}, { passive: true })

Interaction.modes.scaleIndex = function (chart, e, options, useFinalPosition) {
  const axis = options.axis || 'x'
  const isX = axis === 'x'
  const mousePos = isX ? e.x : e.y

  const numLabels = chart.data.labels?.length || 0
  if (numLabels === 0) return []

  let bestIndex = -1
  let bestDist = Infinity

  for (const meta of chart.getSortedVisibleDatasetMetas()) {
    if (meta.hidden) continue
    for (let i = 0; i < meta.data.length && i < numLabels; i++) {
      const el = meta.data[i]
      if (!el) continue
      const center = el.getCenterPoint(useFinalPosition)
      const elPos = isX ? center.x : center.y
      if (isNaN(elPos)) continue
      const dist = Math.abs(mousePos - elPos)
      if (dist < bestDist) {
        bestDist = dist
        bestIndex = i
      }
    }
  }

  if (bestIndex < 0 || bestIndex >= numLabels) return []

  const items = []
  for (const meta of chart.getSortedVisibleDatasetMetas()) {
    if (meta.hidden) continue
    const element = meta.data[bestIndex]
    if (element && !element.skip) {
      items.push({ element, datasetIndex: meta.index, index: bestIndex })
    }
  }
  return items
}

Interaction.modes.nearestByAngle = function (chart, e, options, useFinalPosition) {
  const meta = chart.getDatasetMeta(0)
  if (!meta || !meta.data || !meta.data.length) return []

  const { left, right, top, bottom } = chart.chartArea
  const cx = (left + right) / 2
  const cy = (top + bottom) / 2

  const n = meta.data.length
  const startAngle = ((chart.options.scales?.r?.startAngle || 0) - 90) * Math.PI / 180
  const step = (2 * Math.PI) / n

  const mouseAngle = Math.atan2(e.y - cy, e.x - cx)

  let minDiff = Infinity
  let bestIdx = 0

  for (let i = 0; i < n; i++) {
    const pointAngle = startAngle + i * step
    let diff = mouseAngle - pointAngle
    while (diff > Math.PI) diff -= 2 * Math.PI
    while (diff < -Math.PI) diff += 2 * Math.PI
    if (Math.abs(diff) < minDiff) {
      minDiff = Math.abs(diff)
      bestIdx = i
    }
  }

  const items = []
  for (let di = 0; di < chart.data.datasets.length; di++) {
    const m = chart.getDatasetMeta(di)
    if (m.hidden) continue
    if (m.data[bestIdx]) {
      items.push({ element: m.data[bestIdx], datasetIndex: di, index: bestIdx })
    }
  }

  return items
}

let tooltipEl = null

function ensureTooltipEl() {
  if (!tooltipEl || !document.body.contains(tooltipEl)) {
    tooltipEl = document.createElement('div')
    tooltipEl.id = 'chartjs-tooltip'
    Object.assign(tooltipEl.style, {
      position: 'fixed',
      pointerEvents: 'none',
      zIndex: '99999',
      opacity: '0',
      transition: 'opacity 0.05s ease',
      background: 'rgba(26, 26, 46, 0.95)',
      color: '#fff',
      borderRadius: '6px',
      padding: '8px 12px',
      fontSize: '0.8125rem',
      lineHeight: '1.5',
      fontFamily: 'inherit',
      boxShadow: '0 4px 12px rgba(0,0,0,0.2)',
      maxWidth: '320px',
    })
    document.body.appendChild(tooltipEl)
  }
  return tooltipEl
}

export function externalTooltipHandler(context) {
  const { chart, tooltip } = context
  const el = ensureTooltipEl()

  if (tooltip.opacity === 0) {
    el.style.opacity = '0'
    return
  }

  if (tooltip.body) {
    const titleLines = tooltip.title || []
    const bodyLines = tooltip.body.map(b => b.lines)

    let html = ''

    if (titleLines.length) {
      html += '<div style="font-weight:600;margin-bottom:4px'
      if (bodyLines.length) html += ';border-bottom:1px solid rgba(255,255,255,0.2);padding-bottom:4px'
      html += '">'
      titleLines.forEach(title => { html += `<div>${title}</div>` })
      html += '</div>'
    }

    bodyLines.forEach((lines, i) => {
      const colors = tooltip.labelColors[i]
      const bg = colors?.backgroundColor || 'transparent'
      const border = colors?.borderColor || 'transparent'

      lines.forEach((line, j) => {
        const colorBox = j === 0
          ? `<span style="width:10px;height:10px;min-width:10px;border-radius:2px;background:${bg};border:1px solid ${border};display:inline-block"></span>`
          : '<span style="width:10px;min-width:10px;display:inline-block"></span>'
        html += `<div style="display:flex;align-items:center;gap:6px;padding:1px 0">${colorBox}<span>${line}</span></div>`
      })
    })

    el.innerHTML = html
  }

  const rect = chart.canvas.getBoundingClientRect()
  const scaleX = rect.width / chart.canvas.clientWidth
  const scaleY = rect.height / chart.canvas.clientHeight
  const posX = rect.left + tooltip.caretX * scaleX
  const posY = rect.top + tooltip.caretY * scaleY

  el.style.left = posX + 'px'
  el.style.top = posY + 'px'
  el.style.opacity = '1'

  el.style.transform = posY < 80
    ? 'translate(-50%, 12px)'
    : 'translate(-50%, calc(-100% - 8px))'
}

export const hiddenCanvasTooltip = {
  backgroundColor: 'rgba(0,0,0,0)',
  titleColor: 'rgba(0,0,0,0)',
  bodyColor: 'rgba(0,0,0,0)',
  footerColor: 'rgba(0,0,0,0)',
  borderWidth: 0,
  borderColor: 'rgba(0,0,0,0)',
  padding: 0,
  caretSize: 0,
  displayColors: false,
}
