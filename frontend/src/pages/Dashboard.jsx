import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { authAPI, tutorAPI } from '../services/api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '../components/ui/card';
import { useToast } from '../components/ui/use-toast';
import { Copy, Check } from 'lucide-react';

const Dashboard = () => {
  const [topic, setTopic] = useState('');
  const [responses, setResponses] = useState(() => {
    // Initialize responses from localStorage
    const savedResponses = localStorage.getItem('responses');
    return savedResponses ? JSON.parse(savedResponses) : [];
  });
  const [isLoading, setIsLoading] = useState(false);
  const [username, setUsername] = useState('');
  const [copiedIndex, setCopiedIndex] = useState(null);
  const navigate = useNavigate();
  const { toast } = useToast();

  // Save responses to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem('responses', JSON.stringify(responses));
  }, [responses]);

  useEffect(() => {
    if (!authAPI.isAuthenticated()) {
      navigate('/login');
    } else {
      // Get username from localStorage
      const storedUsername = localStorage.getItem('username');
      setUsername(storedUsername || 'User');
    }
  }, [navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!topic.trim()) return;

    setIsLoading(true);
    try {
      const response = await tutorAPI.askQuestion(topic);
      const newResponse = { 
        question: topic, 
        answer: response,
        timestamp: new Date().toISOString() // Add timestamp for sorting
      };
      setResponses(prev => [...prev, newResponse]);
      setTopic('');
      toast({
        title: "Success",
        description: "Your question has been answered!",
      });
    } catch (error) {
      toast({
        variant: "destructive",
        title: "Error",
        description: error.message || 'Failed to get response',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    authAPI.logout();
    localStorage.removeItem('username'); // Clear username on logout
    localStorage.removeItem('responses'); // Clear responses on logout
    navigate('/login');
  };

  const handleCopy = async (text, index) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedIndex(index);
      toast({
        title: "Copied!",
        description: "Answer copied to clipboard",
      });
      setTimeout(() => setCopiedIndex(null), 2000);
    } catch (err) {
      toast({
        variant: "destructive",
        title: "Error",
        description: "Failed to copy text",
      });
    }
  };

  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="min-h-screen p-4 bg-gradient-to-br from-black via-gray-900 to-gray-800 relative overflow-hidden"
    >
      {/* Background Pattern */}
      <div className="absolute inset-0 bg-[radial-gradient(#e5e7eb_1px,transparent_1px)] [background-size:16px_16px] opacity-5"></div>
      
      {/* Gradient Overlay */}
      <div className="absolute inset-0 bg-gradient-to-tr from-gray-800/20 via-gray-700/10 to-gray-900/20"></div>
      
      {/* Blur Effect */}
      <div className="absolute inset-0 backdrop-blur-[100px]"></div>

      <div className="max-w-4xl mx-auto relative z-10">
        <motion.div 
          initial={{ y: -20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          className="flex items-center justify-between mb-8"
        >
          <div className="flex items-center space-x-4">
            {/* <h1 className="text-3xl font-bold text-white">AI Tutor</h1> */}
            <span className="text-white/90 text-lg font-medium">Welcome, {username}</span>
          </div>
          <Button
            variant="outline"
            onClick={handleLogout}
            className="bg-white/5 text-white hover:bg-white/10 border-white/10 backdrop-blur-sm"
          >
            Logout
          </Button>
        </motion.div>

        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          <Card className="mb-10 bg-white/5 backdrop-blur-sm border-white/10 shadow-xl">
            <CardHeader>
              <CardTitle className="text-white/90">Ask a Question</CardTitle>
              <CardDescription className="text-white/70">
                Enter your question below and get an AI-powered response
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                <Input
                  type="text"
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  placeholder="Enter your question here..."
                  disabled={isLoading}
                  className="bg-white/5 border-white/10 text-white placeholder:text-white/50 focus:border-white/20"
                />
                <Button
                  type="submit"
                  disabled={isLoading || !topic.trim()}
                  className="w-full bg-white/10 hover:bg-white/20 text-white border-white/10"
                >
                  {isLoading ? "Getting Answer..." : "Ask Question"}
                </Button>
              </form>
            </CardContent>
          </Card>
        </motion.div>

        <AnimatePresence>
          <div className="space-y-4">
            {responses.map((response, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
              >
                <Card className="bg-white/5 backdrop-blur-sm border-white/10 shadow-xl hover:bg-white/10 transition-colors duration-200">
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-lg text-white/90">Question: {response.question}</CardTitle>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleCopy(response.answer, index)}
                      className="text-white/90 hover:bg-white/10"
                    >
                      {copiedIndex === index ? (
                        <Check className="h-4 w-4 mr-2" />
                      ) : (
                        <Copy className="h-4 w-4 mr-2" />
                      )}
                      {copiedIndex === index ? 'Copied!' : 'Copy Answer'}
                    </Button>
                  </CardHeader>
                  <CardContent>
                    <p className="whitespace-pre-wrap text-white/80">{response.answer}</p>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </AnimatePresence>
      </div>
    </motion.div>
  );
};

export default Dashboard; 