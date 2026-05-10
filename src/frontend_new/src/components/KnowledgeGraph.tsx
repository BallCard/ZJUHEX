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
      animate: false,
      fit: true,
      padding: 100,
      nodeRepulsion: 400000,
      idealEdgeLength: 150,
      edgeElasticity: 100,
      nestingFactor: 5,
      gravity: 80,
      numIter: 1000,
      initialTemp: 200,
      coolingFactor: 0.95,
      minTemp: 1.0
    };

    cyRef.current = cytoscape({
      container: containerRef.current,
      elements: data,
      zoomingEnabled: true,
      userZoomingEnabled: true,
      panningEnabled: true,
      userPanningEnabled: true,
      minZoom: 0.1,
      maxZoom: 5,
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
              const baseSize = 16;
              const scaleFactor = Math.min(degree * 2.5, 20);
              // 重要类别加大字号
              const categoryBoost = ['disease', 'discipline', 'subdiscipline'].includes(category) ? 4 : 0;
              return `${baseSize + scaleFactor + categoryBoost}px`;
            },
            'text-outline-width': '2px',
            'text-outline-color': '#FFFFFF',
            'text-outline-opacity': 1,
            'text-transform': 'none',
            // Dynamic sizing based on degree
            'width': (node: any) => 60 + Math.min(node.degree() * 8, 80),
            'height': (node: any) => 60 + Math.min(node.degree() * 8, 80),
            'background-color': '#FFFFFF',
            'border-width': (node: any) => node.degree() > 2 ? '5px' : '3px',
            'border-color': (node: any) => {
              const cat = node.data('category');
              switch(cat) {
                case 'concept': return '#667eea';           // 紫蓝色 - 概念
                case 'person': return '#f093fb';            // 粉色 - 人物
                case 'organization': return '#4facfe';      // 天蓝色 - 机构
                case 'disease': return '#EF4444';           // 红色 - 疾病
                case 'discipline': return '#8B5CF6';        // 紫色 - 学科
                case 'subdiscipline': return '#A78BFA';     // 浅紫色 - 子学科
                case 'award': return '#F59E0B';             // 橙色 - 奖项
                case 'attribute': return '#10B981';         // 绿色 - 属性
                case 'project': return '#06B6D4';           // 青色 - 项目
                case 'textbook': return '#EC4899';          // 玫红色 - 教材
                case 'journal': return '#14B8A6';           // 青绿色 - 期刊
                case 'honor': return '#FBBF24';             // 金色 - 荣誉
                case 'course': return '#A855F7';            // 深紫色 - 课程
                default: return '#6B7280';                  // 灰色 - 其他
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
      cyRef.current?.fit(undefined, 80);
      // Apply initial zoom to make nodes more visible
      const currentZoom = cyRef.current?.zoom() || 1;
      cyRef.current?.zoom(currentZoom * 1.5);
      cyRef.current?.center();
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
      cyRef.current?.fit(undefined, 80);
      const currentZoom = cyRef.current?.zoom() || 1;
      cyRef.current?.zoom(currentZoom * 1.5);
      cyRef.current?.center();
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
      cyRef.current?.fit(undefined, 80);
      const currentZoom = cyRef.current?.zoom() || 1;
      cyRef.current?.zoom(currentZoom * 1.5);
      cyRef.current?.center();
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
