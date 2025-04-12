import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { authAPI, tutorAPI } from '../services/api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '../components/ui/card';
import { useToast } from '../components/ui/use-toast';

const Dashboard = () => {
  const [topic, setTopic] = useState('');
  const [responses, setResponses] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [username, setUsername] = useState('');
  const navigate = useNavigate();
  const { toast } = useToast();

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
      setResponses(prev => [...prev, { question: topic, answer: response }]);
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
    navigate('/login');
  };

  return (
    <div className="min-h-screen p-4 bg-black">
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm"></div>
      <div className="max-w-4xl mx-auto relative z-10">
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center space-x-4">
            {/* <h1 className="text-3xl font-bold text-white">AI Tutor</h1> */}
            <span className="text-white text-lg">Welcome, {username}</span>
          </div>
          <Button
            variant="outline"
            onClick={handleLogout}
            className="bg-white/10 text-white hover:bg-white/20 border-white/20"
          >
            Logout
          </Button>
        </div>

        <Card className="mb-10 bg-white/30 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="text-white">Ask a Question</CardTitle>
            <CardDescription className="text-white">
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
                className="bg-white/10 border-white/20 text-white placeholder:text-white/50"
              />
              <Button
                type="submit"
                disabled={isLoading || !topic.trim()}
                className="w-full bg-white/10 hover:bg-white/20 text-white"
              >
                {isLoading ? "Getting Answer..." : "Ask Question"}
              </Button>
            </form>
          </CardContent>
        </Card>

        <div className="space-y-4">
          {responses.map((response, index) => (
            <Card key={index} className="bg-white/30 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-lg text-white">Q: {response.question}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="whitespace-pre-wrap text-white/90">{response.answer}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 