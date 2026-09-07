import { useState } from 'react'
import { ExternalLink, Network } from 'lucide-react'
import { docs, projectNavigation } from '../content/karya'

export function ProjectNavigation() {
  const [exploring, setExploring] = useState(false)

  return (
    <div className="project-navigation">
      <div className="navigation-story">
        <div>
          <span className="eyebrow">FOR MODELS / FIND THE CONTEXT</span>
          <h3>The next Thread should know where to look.</h3>
          <p>
            A living JSON map connects modules, contracts, decisions, and their original sources.
            Models can locate relevant context and inspect dependencies before changing an
            application, without reconstructing the previous conversation.
          </p>
          <pre aria-label="Example project map query">
            <code>{projectNavigation.query}</code>
          </pre>
        </div>
        <ol className="navigation-cycle" aria-label="Living map maintenance cycle">
          {projectNavigation.steps.map(([label, text], index) => (
            <li key={label}>
              <span>{String(index + 1).padStart(2, '0')}</span>
              <div>
                <strong>{label}</strong>
                <p>{text}</p>
              </div>
            </li>
          ))}
        </ol>
      </div>
      <div className="navigation-demo">
        <div className="navigation-demo-heading">
          <div>
            <span className="eyebrow">FOR PEOPLE / EXPLORE THE MAP</span>
            <h3>Karya maps its own project.</h3>
            <p>
              Explore the actual repository map with the viewer delivered to Harness projects.
              Filter areas, inspect connections, rotate the scene, and drag nodes freely.
            </p>
          </div>
          <button
            className="button primary"
            type="button"
            aria-expanded={exploring}
            aria-controls="project-map-demo"
            onClick={() => setExploring((open) => !open)}
          >
            <Network size={18} />{' '}
            {exploring ? 'Close interactive map' : 'Explore the interactive map'}
          </button>
        </div>
        <div id="project-map-demo">
          {exploring ? (
            <iframe
              title="Karya project navigation map"
              src={projectNavigation.viewerUrl}
              className="navigation-map-frame"
              sandbox="allow-scripts"
              loading="lazy"
            />
          ) : null}
        </div>
        <p className="navigation-snapshot-note">
          Website snapshot, regenerated at build time. Colors identify areas and folder tones;
          arrows and source details explain the relationships. Moving nodes changes only the view.
        </p>
        <div className="navigation-links">
          <a
            className="text-link"
            href={projectNavigation.viewerUrl}
            target="_blank"
            rel="noreferrer"
          >
            Open map in a new tab <ExternalLink size={14} />
          </a>
          <a className="text-link" href={docs.navigationJson} target="_blank" rel="noreferrer">
            Inspect the source JSON <ExternalLink size={14} />
          </a>
          <a className="text-link" href={docs.navigationMap} target="_blank" rel="noreferrer">
            Read the maintenance guide <ExternalLink size={14} />
          </a>
        </div>
      </div>
      <p className="navigation-boundary">
        Available through explicit Project Harness adoption for new or established applications.
        Original documents remain authoritative. Checks detect drift; source review verifies the
        relationships. No graph database, background agent, or mandatory RAG service is required.
      </p>
    </div>
  )
}
