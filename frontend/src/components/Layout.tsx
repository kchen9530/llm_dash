import { Link, useLocation } from 'react-router-dom'
import { LayoutDashboard, Rocket, MessageSquare, Activity } from 'lucide-react'
import { cn } from '@/lib/utils'

const navigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'Deploy', href: '/deploy', icon: Rocket },
  { name: 'Chat', href: '/chat', icon: MessageSquare },
]

interface LayoutProps {
  children: React.ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const location = useLocation()

  return (
    <div className="flex h-screen overflow-hidden bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      {/* Sidebar */}
      <div className="hidden md:flex md:w-64 md:flex-col">
        <div className="flex flex-col flex-grow pt-5 overflow-y-auto bg-gray-900/50 backdrop-blur-xl border-r border-gray-800">
          {/* Logo */}
          <div className="flex items-center flex-shrink-0 px-4 mb-8">
            <Activity className="w-8 h-8 text-blue-500 mr-3" />
            <div>
              <h1 className="text-xl font-bold text-white">LLOC</h1>
              <p className="text-xs text-gray-400">LLM Ops Center</p>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-2 space-y-1">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={cn(
                    'group flex items-center px-3 py-3 text-sm font-medium rounded-lg transition-all duration-200',
                    isActive
                      ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/50'
                      : 'text-gray-300 hover:bg-gray-800 hover:text-white'
                  )}
                >
                  <item.icon
                    className={cn(
                      'mr-3 h-5 w-5 flex-shrink-0 transition-transform group-hover:scale-110',
                      isActive ? 'text-white' : 'text-gray-400'
                    )}
                  />
                  {item.name}
                </Link>
              )
            })}
          </nav>

          {/* Footer */}
          <div className="flex-shrink-0 p-4 border-t border-gray-800">
            <div className="text-xs text-gray-500 text-center">
              v1.0.0 | Made with ❤️
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex flex-col flex-1 w-0 overflow-hidden">
        <main className="relative flex-1 overflow-y-auto focus:outline-none">
          <div className="py-6 px-4 sm:px-6 lg:px-8 h-full">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}

