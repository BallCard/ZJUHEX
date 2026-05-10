import React, { useEffect, useRef, useState } from 'react';
import cytoscape from 'cytoscape';

interface Props {
  data: any;
  onNodeClick: (node: any) => void;
}

export const KnowledgeGraph: React.FC<Props> = ({ data, onNodeClick }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<cytoscape.Core | null>(null);
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    if (!containerRef.current || !data) return;

    setIsLoaded(false);

    const layoutConfig = {
      name: 'cose',
      idealEdgeLength: 100,
      nodeOverlap: 20,
      refresh: 20,
      fit: true,
      padding: 50,
      randomize: false,
      componentSpacing: 100,
      nodeRepulsion: 400000,
      edgeElasticity: 100,
      nestingFactor: 5,
      gravity: 80,
      numIter: 1000,
      initialTemp: 200,
      coolingFactor: 0.95,
      minTemp: 1.0,
      animate: false
    };

    cyRef.current = cytoscape({
      container: containerRef.current,
      elements: data,
      zoomingEnabled: true,
      userZoomingEnabled: true,
      panningEnabled: true,
      userPanningEnabled: true,
      minZoom: 0.1,
      maxZoom: 3,
      wheelSensitivity: 0.15,
      style: [
        {
          selector: 'node',
          style: {
            'label': 'data(label)',
            'color': '#1D1D1B',
            'text-valign': 'bottom',
            'text-halign': 'center',
            'text-margin-y': 10,
            'font-family': 'Instrument Sans, sans-serif',
            'font-weight': 'bold',
            'font-size': (node: any) => {
              const degree = node.degree();
              const category = node.data('category');
              const baseSize = 10;
              const scaleFactor = Math.min(degree * 1.5, 12); 
              const categoryBoost = category === '核心机制' ? 2 : 0;
              return `${baseSize + scaleFactor + categoryBoost}px`;
            },
            'text-outline-width': '2px',
            'text-outline-color': '#FFFFFF',
            'text-outline-opacity': 1,
            'text-transform': 'none',
            // Dynamic sizing based on degree
            'width': (node: any) => 24 + Math.min(node.degree() * 4, 30),
            'height': (node: any) => 24 + Math.min(node.degree() * 4, 30),
            'background-color': '#FFFFFF',
            'border-width': (node: any) => node.degree() > 2 ? '4px' : '2px',
            'border-color': (node: any) => {
              const cat = node.data('category');
              switch(cat) {
                case '核心机制': return '#D97757';
                case '评价指标': return '#3B82F6';
                case '基础理论': return '#8B5CF6';
                case '临床表现': return '#EF4444';
                case '治疗方案': return '#10B981';
                case '解剖结构': return '#F59E0B';
                default: return '#6B7280';
              }
            },
            'border-opacity': 0.9,
            'text-wrap': 'wrap',
            'text-max-width': '100px',
            'overlay-padding': '4px',
            'overlay-opacity': 0,
            'ghost': 'yes',
            'ghost-offset-x': 0,
            'ghost-offset-y': 2,
            'ghost-opacity': 0.1,
            'transition-property': 'all',
            'transition-duration': 300,
            'z-index': 1
          }
        },
        {
          selector: 'edge',
          style: {
            'width': 2,
            'line-color': '#CBD5E1',
            'target-arrow-shape': 'triangle',
            'target-arrow-color': '#CBD5E1',
            'curve-style': 'bezier',
            'opacity': 0.4,
            'arrow-scale': 1.2,
            'transition-property': 'opacity, width, line-color',
            'transition-duration': 300
          }
        },
        {
          selector: 'node.dimmed',
          style: {
            'opacity': 0.15,
            'text-opacity': 0.1
          }
        },
        {
          selector: 'edge.dimmed',
          style: {
            'opacity': 0.05
          }
        },
        {
          selector: 'node.highlight',
          style: {
            'border-width': '6px',
            'z-index': 100
          }
        },
        {
          selector: 'edge.highlight',
          style: {
            'width': 4,
            'line-color': '#94A3B8',
            'target-arrow-color': '#94A3B8',
            'opacity': 1,
            'z-index': 50
          }
        }
      ]
    });

    const applyHighlight = (node: any) => {
      if (!cyRef.current) return;
      cyRef.current.elements().addClass('dimmed').removeClass('highlight');
      const neighborhood = node.closedNeighborhood();
      neighborhood.addClass('highlight').removeClass('dimmed');
      neighborhood.edgesWith(neighborhood).addClass('highlight').removeClass('dimmed');
    };

    const clearHighlight = () => {
      // Only clear if no nodes are currently selected
      if (cyRef.current && cyRef.current.elements(':selected').length === 0) {
        cyRef.current.elements().removeClass('dimmed highlight');
      }
    };

    cyRef.current.on('tap', 'node', (evt) => {
      const node = evt.target;
      applyHighlight(node);
      
      const nodeData = node.data();
      // Get detailed neighbors list
      const neighbors = node.neighborhood('node').map((n: any) => ({
        id: n.id(),
        label: n.data('label'),
        category: n.data('category'),
        definition: n.data('definition')
      }));
      
      onNodeClick({
        ...nodeData,
        detailedNeighbors: neighbors
      });
    });

    cyRef.current.on('tap', (evt) => {
      if (evt.target === cyRef.current) {
        cyRef.current?.elements().removeClass('dimmed highlight');
      }
    });

    cyRef.current.on('mouseover', 'node', (evt) => {
      if (containerRef.current) containerRef.current.style.cursor = 'pointer';
      // Only show temporary highlight if nothing is selected
      if (cyRef.current && cyRef.current.elements(':selected').length === 0) {
        applyHighlight(evt.target);
      }
    });

    cyRef.current.on('mouseout', 'node', (evt) => {
      if (containerRef.current) containerRef.current.style.cursor = 'grab';
      clearHighlight();
    });

    // Run layout
    const layout = cyRef.current.layout(layoutConfig);
    
    const handleLayoutStop = () => {
      setIsLoaded(true);
      cyRef.current?.fit(undefined, 50);
    };

    layout.on('layoutstop', handleLayoutStop);
    layout.run();

    // Safety check for synchronous layouts or very fast execution
    if (!layoutConfig.animate) {
      handleLayoutStop();
    }

    // Secondary fallback to ensure visibility
    const timer = setTimeout(() => {
      setIsLoaded(true);
      cyRef.current?.fit(undefined, 50);
    }, 100);

    cyRef.current.ready(() => {
      if (cyRef.current?.elements().length === 0) {
        setIsLoaded(true);
      }
    });

    return () => {
      clearTimeout(timer);
      if (cyRef.current) {
        cyRef.current.destroy();
      }
    };
  }, [data, onNodeClick]);

  useEffect(() => {
    if (!containerRef.current || !cyRef.current) return;
    
    const resizeObserver = new ResizeObserver(() => {
      cyRef.current?.resize();
      cyRef.current?.fit(undefined, 50);
    });
    
    resizeObserver.observe(containerRef.current);
    return () => resizeObserver.disconnect();
  }, []);

  return (
    <div 
      ref={containerRef} 
      className={`w-full h-full min-h-[400px] cursor-grab active:cursor-grabbing transition-opacity duration-300 ease-in-out ${isLoaded ? 'opacity-100' : 'opacity-0'}`} 
    />
  );
};
