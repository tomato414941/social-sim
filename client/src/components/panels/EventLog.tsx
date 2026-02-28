import type { EventResponse } from '../../api/types'

interface Props {
  events: EventResponse[]
  latestEvents: EventResponse[]
}

const categoryIcon: Record<string, string> = {
  disaster: '🌋',
  economic: '📊',
  population: '👥',
}

const categoryClass: Record<string, string> = {
  disaster: 'event-negative',
  economic: 'event-neutral',
  population: 'event-positive',
}

export function EventLog({ events, latestEvents }: Props) {
  const latestIds = new Set(latestEvents.map((e) => e.id + e.description))

  return (
    <div className="event-log">
      <h3>Events</h3>
      {events.length === 0 ? (
        <p className="event-empty">No events yet</p>
      ) : (
        <ul className="event-list">
          {[...events].reverse().map((event, i) => {
            const isNew = latestIds.has(event.id + event.description) && i < latestEvents.length
            return (
              <li
                key={`${event.id}-${i}`}
                className={`event-item ${categoryClass[event.category] || ''} ${isNew ? 'event-new' : ''}`}
              >
                <span className="event-icon">{categoryIcon[event.category] || '📌'}</span>
                <div>
                  <strong>{event.name}</strong>
                  <p>{event.description}</p>
                </div>
              </li>
            )
          })}
        </ul>
      )}
    </div>
  )
}
