import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Toaster } from '@/components/ui/toaster'
import Layout from '@/components/Layout'
import Dashboard from '@/pages/Dashboard'
import Deploy from '@/pages/Deploy'
import Chat from '@/pages/Chat'
import Playground from '@/pages/Playground'

function App() {
  return (
    <Router>
      <div className="dark min-h-screen bg-background">
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/deploy" element={<Deploy />} />
            <Route path="/chat" element={<Chat />} />
            <Route path="/playground" element={<Playground />} />
          </Routes>
        </Layout>
        <Toaster />
      </div>
    </Router>
  )
}

export default App

