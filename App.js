import { useState, useEffect } from "react";
import "@/App.css";
import axios from "axios";
import { Search, Sparkles, TrendingUp, Clock, Target } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { toast } from "sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [vibeQuery, setVibeQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [allProducts, setAllProducts] = useState([]);
  const [queryHistory, setQueryHistory] = useState([]);
  const [isSeeded, setIsSeeded] = useState(false);

  useEffect(() => {
    checkAndSeedProducts();
    loadQueryHistory();
  }, []);

  const checkAndSeedProducts = async () => {
    try {
      const response = await axios.get(`${API}/products`);
      if (response.data.length === 0) {
        await seedProducts();
      } else {
        setAllProducts(response.data);
        setIsSeeded(true);
      }
    } catch (error) {
      console.error("Error checking products:", error);
    }
  };

  const seedProducts = async () => {
    try {
      setLoading(true);
      toast.loading("Setting up fashion catalog...");
      const response = await axios.post(`${API}/products/seed`);
      toast.dismiss();
      toast.success(`${response.data.count} products loaded!`);
      setIsSeeded(true);
      const productsResponse = await axios.get(`${API}/products`);
      setAllProducts(productsResponse.data);
    } catch (error) {
      toast.dismiss();
      toast.error("Failed to load products");
      console.error("Error seeding:", error);
    } finally {
      setLoading(false);
    }
  };

  const loadQueryHistory = async () => {
    try {
      const response = await axios.get(`${API}/metrics`);
      setQueryHistory(response.data.slice(0, 5));
    } catch (error) {
      console.error("Error loading history:", error);
    }
  };

  const handleSearch = async () => {
    if (!vibeQuery.trim()) {
      toast.error("Please enter a vibe query");
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API}/search`, {
        vibe: vibeQuery,
        limit: 3,
        threshold: 0.7
      });

      setSearchResults(response.data.results);
      setMetrics(response.data.metrics);
      loadQueryHistory();

      if (response.data.results.length === 0) {
        toast.info(response.data.metrics.message);
      } else {
        toast.success(response.data.metrics.message);
      }
    } catch (error) {
      toast.error("Search failed. Please try again.");
      console.error("Search error:", error);
    } finally {
      setLoading(false);
    }
  };

  const sampleQueries = [
    "energetic urban chic",
    "cozy comfortable loungewear",
    "professional sophisticated style",
    "casual festival boho vibes"
  ];

  return (
    <div className="App">
      <div className="min-h-screen">
        {/* Hero Section */}
        <div className="hero-section">
          <div className="hero-content">
            <div className="flex items-center justify-center gap-3 mb-4">
              <Sparkles className="w-10 h-10 text-rose-400" />
              <h1 className="hero-title">Vibe Matcher</h1>
            </div>
            <p className="hero-subtitle">
              AI-powered fashion recommendation using semantic similarity
            </p>
            <div className="search-container">
              <div className="search-wrapper">
                <Search className="search-icon" />
                <Input
                  data-testid="vibe-search-input"
                  placeholder="Describe your style vibe... e.g., 'cozy autumn vibes'"
                  value={vibeQuery}
                  onChange={(e) => setVibeQuery(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                  className="search-input"
                />
              </div>
              <Button 
                data-testid="search-button"
                onClick={handleSearch} 
                disabled={loading}
                className="search-button"
              >
                {loading ? "Matching..." : "Find Matches"}
              </Button>
            </div>

            {/* Sample Queries */}
            <div className="sample-queries">
              <p className="text-sm text-slate-600 mb-2">Try these vibes:</p>
              <div className="flex flex-wrap gap-2 justify-center">
                {sampleQueries.map((query, idx) => (
                  <Badge
                    key={idx}
                    data-testid={`sample-query-${idx}`}
                    variant="outline"
                    className="cursor-pointer hover:bg-rose-50 hover:border-rose-300 transition-all duration-200"
                    onClick={() => setVibeQuery(query)}
                  >
                    {query}
                  </Badge>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="main-content">
          <Tabs defaultValue="results" className="w-full">
            <TabsList className="grid w-full max-w-md mx-auto grid-cols-3 mb-8">
              <TabsTrigger value="results" data-testid="results-tab">Top Matches</TabsTrigger>
              <TabsTrigger value="metrics" data-testid="metrics-tab">Metrics</TabsTrigger>
              <TabsTrigger value="catalog" data-testid="catalog-tab">Catalog</TabsTrigger>
            </TabsList>

            {/* Results Tab */}
            <TabsContent value="results" data-testid="results-content">
              {searchResults.length > 0 ? (
                <div>
                  <div className="text-center mb-8">
                    <h2 className="text-2xl font-semibold text-slate-800 mb-2">
                      Top 3 Matches for "{metrics?.query}"
                    </h2>
                    <p className="text-slate-600">
                      Found {searchResults.length} items • Latency: {metrics?.latency_ms}ms
                    </p>
                  </div>
                  <div className="results-grid">
                    {searchResults.map((result, idx) => (
                      <Card key={result.id} className="product-card" data-testid={`result-card-${idx}`}>
                        <div className="product-image-container">
                          <img 
                            src={result.image_url || "https://via.placeholder.com/400x500?text=Fashion+Item"} 
                            alt={result.name}
                            className="product-image"
                          />
                          <div className="similarity-badge">
                            <Target className="w-4 h-4" />
                            {(result.similarity_score * 100).toFixed(1)}% match
                          </div>
                        </div>
                        <CardHeader>
                          <CardTitle className="text-xl">{result.name}</CardTitle>
                          <CardDescription className="text-sm">{result.category}</CardDescription>
                        </CardHeader>
                        <CardContent>
                          <p className="text-slate-700 mb-4 text-sm leading-relaxed">
                            {result.description}
                          </p>
                          <div className="flex flex-wrap gap-2">
                            {result.vibe_tags.map((tag, tidx) => (
                              <Badge key={tidx} variant="secondary" className="text-xs">
                                {tag}
                              </Badge>
                            ))}
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="empty-state" data-testid="empty-results">
                  <Sparkles className="w-16 h-16 text-slate-300 mb-4" />
                  <h3 className="text-xl font-semibold text-slate-700 mb-2">
                    No matches yet
                  </h3>
                  <p className="text-slate-500">
                    Search for your style vibe to discover fashion recommendations
                  </p>
                </div>
              )}
            </TabsContent>

            {/* Metrics Tab */}
            <TabsContent value="metrics" data-testid="metrics-content">
              <div className="max-w-4xl mx-auto space-y-6">
                {metrics && (
                  <Card className="glass-card">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <TrendingUp className="w-5 h-5 text-emerald-500" />
                        Current Search Metrics
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                        <div className="metric-item">
                          <p className="text-sm text-slate-600 mb-1">Results</p>
                          <p className="text-2xl font-bold text-slate-800">{metrics.results_count}</p>
                        </div>
                        <div className="metric-item">
                          <p className="text-sm text-slate-600 mb-1">Latency</p>
                          <p className="text-2xl font-bold text-slate-800">{metrics.latency_ms}ms</p>
                        </div>
                        <div className="metric-item">
                          <p className="text-sm text-slate-600 mb-1">Top Score</p>
                          <p className="text-2xl font-bold text-slate-800">
                            {metrics.top_score ? (metrics.top_score * 100).toFixed(1) + '%' : 'N/A'}
                          </p>
                        </div>
                        <div className="metric-item">
                          <p className="text-sm text-slate-600 mb-1">Threshold</p>
                          <p className="text-2xl font-bold text-slate-800">{(metrics.threshold_used * 100).toFixed(0)}%</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                )}

                {queryHistory.length > 0 && (
                  <Card className="glass-card">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Clock className="w-5 h-5 text-blue-500" />
                        Recent Searches
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        {queryHistory.map((item, idx) => (
                          <div key={idx} className="history-item" data-testid={`history-item-${idx}`}>
                            <div className="flex-1">
                              <p className="font-medium text-slate-800">{item.query}</p>
                              <p className="text-sm text-slate-500">
                                {item.results_count} results • {item.latency_ms}ms
                              </p>
                            </div>
                            {item.top_score && (
                              <Badge variant="outline">
                                {(item.top_score * 100).toFixed(1)}%
                              </Badge>
                            )}
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}
              </div>
            </TabsContent>

            {/* Catalog Tab */}
            <TabsContent value="catalog" data-testid="catalog-content">
              <div>
                <div className="text-center mb-8">
                  <h2 className="text-2xl font-semibold text-slate-800 mb-2">
                    Fashion Catalog
                  </h2>
                  <p className="text-slate-600">
                    {allProducts.length} products available for matching
                  </p>
                </div>
                <div className="catalog-grid">
                  {allProducts.map((product, idx) => (
                    <Card key={product.id} className="catalog-card" data-testid={`catalog-item-${idx}`}>
                      <div className="catalog-image-container">
                        <img 
                          src={product.image_url || "https://via.placeholder.com/300x400?text=Fashion"} 
                          alt={product.name}
                          className="catalog-image"
                        />
                      </div>
                      <CardHeader className="pb-3">
                        <CardTitle className="text-lg">{product.name}</CardTitle>
                        <CardDescription className="text-xs uppercase tracking-wide">
                          {product.category}
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <p className="text-slate-600 text-sm mb-3 line-clamp-2">
                          {product.description}
                        </p>
                        <div className="flex flex-wrap gap-1">
                          {product.vibe_tags.slice(0, 3).map((tag, tidx) => (
                            <Badge key={tidx} variant="secondary" className="text-xs">
                              {tag}
                            </Badge>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
}

export default App;