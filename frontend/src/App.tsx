import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Toaster } from '@/components/ui/toaster'
import Layout from '@/components/Layout'
import Dashboard from '@/pages/Dashboard'
import Deploy from '@/pages/Deploy'
import Chat from '@/pages/Chat'
import Transform from '@/pages/Transform'
import PhotoSearch from '@/pages/PhotoSearch'
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
            <Route path="/transform" element={<Transform />} />
            <Route path="/playground" element={<Playground />} />
            <Route path="/photos" element={<PhotoSearch />} />
          </Routes>
        </Layout>
        <Toaster />
      </div>
    </Router>
  )
}

export default App

