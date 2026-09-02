import { useRef, useEffect, useState } from 'react';
import * as d3 from 'd3';

const NODE_COLORS = {
  Username: '#e63946',
  PGPKey: '#9d4edd',
  Wallet: '#00f5d4',
  Domain: '#3a86ff',
  Post: '#ffb703',
  Source: '#8d99ae',
};

const NODE_SIZES = {
  Username: 18,
  PGPKey: 13,
  Wallet: 13,
  Domain: 12,
  Post: 6,
  Source: 9,
};

export default function ForceGraph({ data, height = 550, onNodeClick }) {
  const svgRef = useRef(null);
  const tooltipRef = useRef(null);
  const [showPosts, setShowPosts] = useState(false);

  useEffect(() => {
    if (!data || !data.nodes || !data.nodes.length) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const container = svgRef.current.parentElement;
    const width = container.clientWidth;

    // Filter out Post nodes by default for cleaner visualization
    let nodes = data.nodes;
    let links = data.links;
    if (!showPosts) {
      const postIds = new Set(nodes.filter(n => n.type === 'Post').map(n => n.id));
      nodes = nodes.filter(n => n.type !== 'Post');
      links = links.filter(l => !postIds.has(l.source) && !postIds.has(l.target) &&
                                  !postIds.has(l.source?.id) && !postIds.has(l.target?.id));
    }

    // Deep clone to avoid D3 mutation issues
    const simNodes = nodes.map(d => ({ ...d }));
    const simLinks = links.map(d => ({ ...d }));

    // Zoom behavior
    const zoom = d3.zoom()
      .scaleExtent([0.2, 5])
      .on('zoom', (event) => {
        g.attr('transform', event.transform);
      });

    svg.attr('width', width).attr('height', height).call(zoom);

    const g = svg.append('g');

    // Simulation
    const simulation = d3.forceSimulation(simNodes)
      .force('link', d3.forceLink(simLinks).id(d => d.id).distance(70))
      .force('charge', d3.forceManyBody().strength(-200))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(d => (NODE_SIZES[d.type] || 10) + 4));

    // Links
    const link = g.append('g')
      .selectAll('line')
      .data(simLinks)
      .join('line')
      .attr('stroke', '#334155')
      .attr('stroke-width', 1.5)
      .attr('stroke-opacity', 0.6);

    // Link labels
    const linkLabel = g.append('g')
      .selectAll('text')
      .data(simLinks)
      .join('text')
      .text(d => d.rel_type)
      .attr('font-size', '8px')
      .attr('fill', '#64748b')
      .attr('text-anchor', 'middle')
      .attr('dy', -4);

    // Nodes
    const node = g.append('g')
      .selectAll('circle')
      .data(simNodes)
      .join('circle')
      .attr('r', d => NODE_SIZES[d.type] || 10)
      .attr('fill', d => NODE_COLORS[d.type] || '#8d99ae')
      .attr('stroke', '#0b0f19')
      .attr('stroke-width', 2)
      .style('cursor', 'pointer')
      .call(d3.drag()
        .on('start', (event, d) => {
          if (!event.active) simulation.alphaTarget(0.3).restart();
          d.fx = d.x;
          d.fy = d.y;
        })
        .on('drag', (event, d) => {
          d.fx = event.x;
          d.fy = event.y;
        })
        .on('end', (event, d) => {
          if (!event.active) simulation.alphaTarget(0);
          d.fx = null;
          d.fy = null;
        })
      );

    // Node labels
    const label = g.append('g')
      .selectAll('text')
      .data(simNodes)
      .join('text')
      .text(d => d.type === 'Post' ? '' : d.label)
      .attr('font-size', d => d.type === 'Username' ? '11px' : '9px')
      .attr('font-weight', d => d.type === 'Username' ? '700' : '400')
      .attr('fill', '#e2e8f0')
      .attr('text-anchor', 'middle')
      .attr('dy', d => (NODE_SIZES[d.type] || 10) + 14)
      .style('pointer-events', 'none');

    // Tooltip
    const tooltip = d3.select(tooltipRef.current);

    // Hover effects
    node.on('mouseover', (event, d) => {
      // Highlight connected
      const connected = new Set();
      simLinks.forEach(l => {
        const sId = typeof l.source === 'object' ? l.source.id : l.source;
        const tId = typeof l.target === 'object' ? l.target.id : l.target;
        if (sId === d.id) connected.add(tId);
        if (tId === d.id) connected.add(sId);
      });
      connected.add(d.id);

      node.attr('opacity', n => connected.has(n.id) ? 1 : 0.15);
      link.attr('opacity', l => {
        const sId = typeof l.source === 'object' ? l.source.id : l.source;
        const tId = typeof l.target === 'object' ? l.target.id : l.target;
        return (sId === d.id || tId === d.id) ? 1 : 0.05;
      });
      label.attr('opacity', n => connected.has(n.id) ? 1 : 0.1);

      tooltip
        .style('display', 'block')
        .style('left', (event.pageX + 12) + 'px')
        .style('top', (event.pageY - 12) + 'px')
        .html(`<strong>${d.type}</strong><br/>${d.label}<br/><span style="color:#64748b">${d.title || ''}</span>`);
    })
    .on('mouseout', () => {
      node.attr('opacity', 1);
      link.attr('opacity', 0.6);
      label.attr('opacity', 1);
      tooltip.style('display', 'none');
    })
    .on('click', (event, d) => {
      if (onNodeClick && d.type === 'Username') {
        onNodeClick(d.id);
      }
    });

    // Tick
    simulation.on('tick', () => {
      link
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y);

      linkLabel
        .attr('x', d => (d.source.x + d.target.x) / 2)
        .attr('y', d => (d.source.y + d.target.y) / 2);

      node.attr('cx', d => d.x).attr('cy', d => d.y);
      label.attr('x', d => d.x).attr('y', d => d.y);
    });

    // Initial zoom to fit
    setTimeout(() => {
      const bounds = g.node().getBBox();
      if (bounds.width > 0 && bounds.height > 0) {
        const scale = Math.min(width / (bounds.width + 80), height / (bounds.height + 80), 1.5);
        const tx = width / 2 - (bounds.x + bounds.width / 2) * scale;
        const ty = height / 2 - (bounds.y + bounds.height / 2) * scale;
        svg.transition().duration(500).call(
          zoom.transform,
          d3.zoomIdentity.translate(tx, ty).scale(scale)
        );
      }
    }, 1500);

    return () => simulation.stop();
  }, [data, height, showPosts, onNodeClick]);

  return (
    <div className="graph-container" style={{ height: height + 'px', position: 'relative' }}>
      <svg ref={svgRef}></svg>

      {/* Legend */}
      <div className="graph-legend">
        {Object.entries(NODE_COLORS).map(([type, color]) => (
          <div key={type} className="legend-item">
            <span className="legend-dot" style={{ background: color }}></span>
            <span>{type}</span>
          </div>
        ))}
      </div>

      {/* Controls */}
      <div className="absolute top-4 right-4 flex gap-2 z-10">
        <button
          className={`btn-outline text-xs px-3 py-1 ${showPosts ? 'border-cyber-blue text-cyber-blue' : ''}`}
          onClick={() => setShowPosts(!showPosts)}
        >
          {showPosts ? 'Hide Posts' : 'Show Posts'}
        </button>
      </div>

      {/* Tooltip */}
      <div ref={tooltipRef} className="graph-tooltip" style={{ display: 'none' }}></div>
    </div>
  );
}
