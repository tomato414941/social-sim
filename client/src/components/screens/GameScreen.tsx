import type { GameState } from '../../hooks/useGame'
import type { PolicySet } from '../../api/types'
import { Header } from '../layout/Header'
import { PolicyPanel } from '../panels/PolicyPanel'
import { StatsPanel } from '../panels/StatsPanel'
import { ScoreBar } from '../panels/ScoreBar'
import { EventLog } from '../panels/EventLog'
import { GiniChart } from '../charts/GiniChart'
import { WealthChart } from '../charts/WealthChart'
import { DistributionChart } from '../charts/DistributionChart'

interface Props {
  game: GameState
  onAdvanceTurn: () => void
  onPolicyChange: (changes: Partial<PolicySet>) => void
}

export function GameScreen({ game, onAdvanceTurn, onPolicyChange }: Props) {
  return (
    <div className="game-layout">
      <Header turn={game.turn} maxTurns={game.maxTurns} scores={game.scores} />

      <div className="game-body">
        <PolicyPanel
          policies={game.policies}
          onChange={onPolicyChange}
          onAdvanceTurn={onAdvanceTurn}
          isLoading={game.isLoading}
          isFinished={game.phase === 'finished'}
        />

        <main className="game-main">
          {game.state && (
            <>
              <StatsPanel state={game.state} />

              <div className="charts-grid">
                <GiniChart data={game.history.gini} />
                <WealthChart
                  wealth={game.history.mean_wealth}
                  happiness={game.history.mean_happiness}
                />
                <DistributionChart distribution={game.state.wealth_distribution} />
              </div>

              {game.scores && <ScoreBar scores={game.scores} />}

              <EventLog events={game.allEvents} latestEvents={game.events} />
            </>
          )}

          {game.error && <div className="error-banner">{game.error}</div>}
        </main>
      </div>
    </div>
  )
}
