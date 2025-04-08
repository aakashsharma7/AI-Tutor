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
  const navigate = useNavigate();
  const { toast } = useToast();

  useEffect(() => {
    if (!authAPI.isAuthenticated()) {
      navigate('/login');
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

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setIsLoading(true);
    try {
      const response = await tutorAPI.uploadDocument(file);
      setResponses(prev => [...prev, { question: 'Document Upload', answer: response }]);
      toast({
        title: "Success",
        description: "Document uploaded successfully!",
      });
    } catch (error) {
      toast({
        variant: "destructive",
        title: "Error",
        description: error.message || 'Failed to upload document',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    authAPI.logout();
    navigate('/login');
  };

  return (
    <div 
      className="min-h-screen p-4"
      style={{
        backgroundImage: "url('https://images.unsplash.com/photo-1516321318423-f06f85e504b3?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80')",
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat',
        backgroundAttachment: 'fixed',
      }}
    >
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm"></div>
      <div className="max-w-4xl mx-auto relative z-10">
        <div className="flex items-center justify-center">
          <h1 className="text-3xl font-bold text-white ">AI Tutor Dashboard</h1>
          <Button
            variant="outline"
            onClick={handleLogout}
            className="bg-white text-gray-800 hover:bg-blue-50 m-8 right-8"
          >
            Logout
          </Button>
        </div>

        <Card className="mb-8 bg-white/90 backdrop-blur-sm">
          <CardHeader>
            <CardTitle>Ask a Question</CardTitle>
            <CardDescription>
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
              />
              <Button
                type="submit"
                disabled={isLoading || !topic.trim()}
                className="w-full"
              >
                {isLoading ? "Getting Answer..." : "Ask Question"}
              </Button>
            </form>
          </CardContent>
        </Card>

        <Card className="mb-8 bg-white/90 backdrop-blur-sm">
          <CardHeader>
            <CardTitle>Upload Document</CardTitle>
            <CardDescription>
              Upload a document for the AI to analyze
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Input
              type="file"
              onChange={handleFileUpload}
              disabled={isLoading}
              accept=".pdf,.doc,.docx,.txt"
            />
          </CardContent>
        </Card>

        <div className="space-y-4">
          {responses.map((response, index) => (
            <Card key={index} className="bg-white/90 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-lg">Q: {response.question}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="whitespace-pre-wrap">{response.answer}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 