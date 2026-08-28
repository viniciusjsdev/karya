import { useEffect, useState } from 'react'
import { Github, Menu, Moon, Sun, X } from 'lucide-react'
import { navigation, repositoryUrl } from '../content/karya'

type HeaderProps = {
  theme: 'amphora' | 'papyrus'
  onThemeChange: () => void
}

export function Header({ theme, onThemeChange }: HeaderProps) {
  const [menuOpen, setMenuOpen] = useState(false)
  const [activeId, setActiveId] = useState('concept')

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((entry) => entry.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0]
        if (visible?.target.id) setActiveId(visible.target.id)
      },
      { rootMargin: '-20% 0px -65% 0px', threshold: [0, 0.15, 0.4] },
    )
    navigation.forEach(({ id }) => {
      const element = document.getElementById(id)
      if (element) observer.observe(element)
    })
    return () => observer.disconnect()
  }, [])

  return (
    <header className="site-header">
      <div className="header-inner">
        <a className="brand-link" href="#concept" aria-label="Karya home">
          <img
            src={`brand/icon/karya-icon-${theme === 'amphora' ? 'dark' : 'light'}-64.png`}
            alt=""
            width="38"
            height="38"
          />
          <span>KARYA</span>
        </a>
        <nav className="desktop-nav" aria-label="Primary navigation">
          {navigation.map((item) => (
            <a
              key={item.id}
              href={`#${item.id}`}
              aria-current={activeId === item.id ? 'location' : undefined}
            >
              {item.label}
            </a>
          ))}
        </nav>
        <div className="header-actions">
          <button
            className="icon-button"
            type="button"
            onClick={onThemeChange}
            aria-label={`Use ${theme === 'amphora' ? 'Papyrus' : 'Amphora'} theme`}
          >
            {theme === 'amphora' ? <Sun size={18} /> : <Moon size={18} />}
          </button>
          <a
            className="icon-button desktop-only"
            href={repositoryUrl}
            target="_blank"
            rel="noreferrer"
            aria-label="View Karya on GitHub"
          >
            <Github size={18} />
          </a>
          <button
            className="icon-button menu-button"
            type="button"
            onClick={() => setMenuOpen((open) => !open)}
            aria-expanded={menuOpen}
            aria-controls="mobile-navigation"
            aria-label="Toggle navigation"
          >
            {menuOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>
      </div>
      {menuOpen ? (
        <nav id="mobile-navigation" className="mobile-nav" aria-label="Mobile navigation">
          {navigation.map((item) => (
            <a key={item.id} href={`#${item.id}`} onClick={() => setMenuOpen(false)}>
              {item.label}
            </a>
          ))}
          <a href={repositoryUrl} target="_blank" rel="noreferrer">
            GitHub
          </a>
        </nav>
      ) : null}
    </header>
  )
}
