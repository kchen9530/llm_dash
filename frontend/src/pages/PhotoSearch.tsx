import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useToast } from '@/components/ui/use-toast'
import { useModelStore } from '@/store/useModelStore'
import { Search, Image as ImageIcon, Loader2, Sparkles, Info } from 'lucide-react'

interface Photo {
  id: string
  filename: string
  description: string
  tags: string[]
}

interface SearchResult {
  photo_id: string
  filename: string
  description: string
  tags: string[]
  similarity: number
  similarity_percent: number
}

export default function PhotoSearch() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SearchResult[]>([])
  const [allPhotos, setAllPhotos] = useState<Photo[]>([])
  const [loading, setLoading] = useState(false)
  const [initialized, setInitialized] = useState(false)
  const [initializing, setInitializing] = useState(false)
  const { models } = useModelStore()
  const { toast } = useToast()

  // Get deployed embedding models
  const embeddingModels = models.filter((m) => {
    if (m.status !== 'RUNNING') return false
    const name = m.model_name.toLowerCase()
    return name.includes('embed') ||
           name.includes('sentence-transformers') ||
           name.includes('bge-') ||
           name.includes('minilm')
  })

  useEffect(() => {
    fetchAllPhotos()
    checkInitialization()
  }, [])

  const fetchAllPhotos = async () => {
    try {
      const response = await fetch('http://localhost:7860/api/photos/photos')
      const data = await response.json()
      setAllPhotos(data.photos)
    } catch (error) {
      console.error('Failed to fetch photos:', error)
    }
  }

  const checkInitialization = async () => {
    try {
      const response = await fetch('http://localhost:7860/api/photos/stats')
      const data = await response.json()
      setInitialized(data.embeddings_initialized)
    } catch (error) {
      console.error('Failed to check initialization:', error)
    }
  }

  const handleInitialize = async () => {
    setInitializing(true)
    try {
      const response = await fetch('http://localhost:7860/api/photos/initialize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      })
      
      if (!response.ok) throw new Error('Initialization failed')
      
      const data = await response.json()
      setInitialized(true)
      
      toast({
        title: 'Initialized!',
        description: `Loaded ${data.stats.total_photos} photos with ${data.stats.embedding_dimension}D embeddings`,
      })
    } catch (error: any) {
      toast({
        title: 'Initialization Failed',
        description: error.message,
        variant: 'destructive',
      })
    } finally {
      setInitializing(false)
    }
  }

  const handleSearch = async () => {
    if (!query.trim()) {
      toast({
        title: 'Query Required',
        description: 'Please enter a search query',
        variant: 'destructive',
      })
      return
    }

    if (!initialized) {
      toast({
        title: 'Not Initialized',
        description: 'Please initialize the photo search first',
        variant: 'destructive',
      })
      return
    }

    setLoading(true)
    try {
      const response = await fetch('http://localhost:7860/api/photos/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: query.trim(),
          top_k: 5,
        }),
      })

      if (!response.ok) throw new Error('Search failed')

      const data = await response.json()
      setResults(data.results)
      
      toast({
        title: 'Search Complete',
        description: `Found ${data.total_results} matching photos`,
      })
    } catch (error: any) {
      toast({
        title: 'Search Failed',
        description: error.message,
        variant: 'destructive',
      })
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && query.trim() && initialized) {
      handleSearch()
    }
  }

  // Photo icon component (using emoji as placeholder)
  const PhotoCard = ({ result }: { result: SearchResult }) => {
    // Determine emoji based on filename/tags
    const getEmoji = () => {
      const name = result.filename.toLowerCase()
      const tags = result.tags.join(' ').toLowerCase()
      
      if (name.includes('cat') || tags.includes('cat')) return '🐱'
      if (name.includes('dog') || tags.includes('dog')) return '🐕'
      return '🖼️'
    }

    const getSimilarityColor = (percent: number) => {
      if (percent >= 80) return 'text-green-400'
      if (percent >= 60) return 'text-blue-400'
      if (percent >= 40) return 'text-yellow-400'
      return 'text-gray-400'
    }

    return (
      <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden hover:border-blue-500 transition-all">
        {/* Photo Preview */}
        <div className="bg-gradient-to-br from-gray-700 to-gray-800 h-48 flex items-center justify-center text-8xl">
          {getEmoji()}
        </div>
        
        {/* Photo Info */}
        <div className="p-4">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-semibold text-white truncate flex-1">
              {result.filename}
            </h3>
            <span className={`text-lg font-bold ${getSimilarityColor(result.similarity_percent)}`}>
              {result.similarity_percent.toFixed(1)}%
            </span>
          </div>
          
          <p className="text-sm text-gray-400 mb-3 line-clamp-2">
            {result.description}
          </p>
          
          <div className="flex flex-wrap gap-1">
            {result.tags.map((tag, idx) => (
              <span
                key={idx}
                className="px-2 py-1 bg-blue-900/30 text-blue-300 text-xs rounded-full"
              >
                #{tag}
              </span>
            ))}
          </div>
        </div>
      </div>
    )
  }

  const examples = [
    'a black dog',
    'cat playing',
    'dog running on beach',
    'sleeping cat',
    'white fluffy dog',
  ]

  return (
    <div className="h-full flex flex-col space-y-4">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-white">Photo Search</h1>
          <p className="text-gray-400 mt-1">Semantic image search using text embeddings</p>
        </div>
        {!initialized && (
          <Button
            onClick={handleInitialize}
            disabled={initializing}
            className="bg-purple-600 hover:bg-purple-700"
          >
            {initializing ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Initializing...
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4 mr-2" />
                Initialize Search
              </>
            )}
          </Button>
        )}
        {initialized && (
          <div className="px-3 py-1 bg-green-900 text-green-300 rounded-full text-sm">
            ✓ Ready ({allPhotos.length} photos)
          </div>
        )}
      </div>

      {/* Search Bar */}
      <Card className="glass border-gray-800">
        <CardContent className="pt-6">
          <div className="flex gap-2">
            <Input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Search for photos (e.g., 'a black dog', 'cat playing')..."
              className="bg-gray-800 border-gray-700 text-white flex-1 h-12 text-base"
              disabled={!initialized}
            />
            <Button
              onClick={handleSearch}
              disabled={!query.trim() || !initialized || loading}
              className="bg-blue-600 hover:bg-blue-700 h-12 px-6"
            >
              {loading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <>
                  <Search className="w-5 h-5 mr-2" />
                  Search
                </>
              )}
            </Button>
          </div>

          {/* Examples */}
          <div className="mt-3 flex items-center gap-2 flex-wrap">
            <span className="text-xs text-gray-500">Try:</span>
            {examples.map((example, idx) => (
              <button
                key={idx}
                onClick={() => setQuery(example)}
                className="text-xs text-blue-400 hover:text-blue-300 hover:underline"
                disabled={!initialized}
              >
                "{example}"
              </button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Info Banner */}
      {!initialized && (
        <Card className="glass border-yellow-900 bg-yellow-900/10">
          <CardContent className="pt-4">
            <div className="flex items-start gap-3">
              <Info className="w-5 h-5 text-yellow-400 mt-0.5" />
              <div className="flex-1">
                <p className="text-yellow-300 text-sm font-semibold">Setup Required</p>
                <p className="text-yellow-400/80 text-xs mt-1">
                  {embeddingModels.length > 0 ? (
                    <>
                      Click "Initialize Search" to use your deployed embedding model ({embeddingModels[0].model_name}) 
                      and compute photo embeddings. Takes ~10 seconds.
                    </>
                  ) : (
                    <>
                      First deploy an embedding model (e.g., sentence-transformers/all-MiniLM-L6-v2) 
                      from the Deploy tab, then initialize photo search here. 
                      First time takes 1-2 minutes to download (~80MB).
                    </>
                  )}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Results */}
      {results.length > 0 && (
        <Card className="glass border-gray-800 flex-1 overflow-hidden flex flex-col">
          <CardHeader>
            <CardTitle className="text-white flex items-center">
              <ImageIcon className="w-5 h-5 mr-2 text-purple-400" />
              Search Results
            </CardTitle>
            <CardDescription>
              Found {results.length} photos matching "{query}"
            </CardDescription>
          </CardHeader>
          <CardContent className="flex-1 overflow-y-auto">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {results.map((result) => (
                <PhotoCard key={result.photo_id} result={result} />
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* All Photos View (when no search) */}
      {results.length === 0 && initialized && !loading && (
        <Card className="glass border-gray-800 flex-1 overflow-hidden flex flex-col">
          <CardHeader>
            <CardTitle className="text-white flex items-center">
              <ImageIcon className="w-5 h-5 mr-2 text-gray-400" />
              Photo Database
            </CardTitle>
            <CardDescription>
              {allPhotos.length} photos available. Enter a search query to find similar images.
            </CardDescription>
          </CardHeader>
          <CardContent className="flex-1 overflow-y-auto">
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
              {allPhotos.map((photo) => {
                const getEmoji = () => {
                  const tags = photo.tags.join(' ').toLowerCase()
                  if (tags.includes('cat')) return '🐱'
                  if (tags.includes('dog')) return '🐕'
                  return '🖼️'
                }

                return (
                  <div
                    key={photo.id}
                    className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden hover:border-gray-600 transition-all"
                  >
                    <div className="bg-gradient-to-br from-gray-700 to-gray-800 h-32 flex items-center justify-center text-5xl">
                      {getEmoji()}
                    </div>
                    <div className="p-2">
                      <p className="text-xs text-gray-400 truncate">
                        {photo.filename}
                      </p>
                    </div>
                  </div>
                )
              })}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Empty State */}
      {results.length === 0 && !initialized && !allPhotos.length && (
        <Card className="glass border-gray-800 flex-1 flex items-center justify-center">
          <div className="text-center">
            <ImageIcon className="w-16 h-16 mx-auto mb-4 text-gray-700" />
            <p className="text-gray-500">Initialize photo search to get started</p>
          </div>
        </Card>
      )}
    </div>
  )
}

