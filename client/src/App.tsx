import { useGame } from './hooks/useGame'
import { StartScreen } from './components/screens/StartScreen'
import { GameScreen } from './components/screens/GameScreen'
import { ResultScreen } from './components/screens/ResultScreen'
import './App.css'

function App() {
  const { state, startGame, nextTurn, updatePolicies, resetGame } = useGame()

  if (state.phase === 'start') {
    return <StartScreen onStart={startGame} isLoading={state.isLoading} />
  }

  if (state.phase === 'finished' && state.scores) {
    return (
      <ResultScreen
        scores={state.scores}
        history={state.history}
        turn={state.turn}
        onPlayAgain={resetGame}
      />
    )
  }

  return (
    <GameScreen
      game={state}
      onAdvanceTurn={nextTurn}
      onPolicyChange={updatePolicies}
    />
  )
}

export default App
