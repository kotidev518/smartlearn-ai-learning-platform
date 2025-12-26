import React, { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import axios from 'axios';
import { Navbar } from '@/components/Navbar';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Label } from '@/components/ui/label';
import { Progress } from '@/components/ui/progress';
import { ArrowLeft, CheckCircle2, XCircle } from 'lucide-react';
import { motion } from 'framer-motion';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const VideoPlayerPage = () => {
  const { videoId } = useParams();
  const { getAxiosConfig } = useAuth();
  const navigate = useNavigate();
  const videoRef = useRef(null);
  
  const [video, setVideo] = useState(null);
  const [quiz, setQuiz] = useState(null);
  const [watchProgress, setWatchProgress] = useState(0);
  const [showQuiz, setShowQuiz] = useState(false);
  const [quizAnswers, setQuizAnswers] = useState([]);
  const [quizResult, setQuizResult] = useState(null);
  const [nextVideo, setNextVideo] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchVideoData();
  }, [videoId]);

  useEffect(() => {
    const interval = setInterval(() => {
      if (videoRef.current && !videoRef.current.paused) {
        const progress = (videoRef.current.currentTime / videoRef.current.duration) * 100;
        setWatchProgress(progress);
        
        // Update progress every 10%
        if (progress % 10 < 1) {
          updateProgress(progress);
        }
      }
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  const fetchVideoData = async () => {
    try {
      const [videoRes, progressRes] = await Promise.all([
        axios.get(`${API}/videos/${videoId}`, getAxiosConfig()),
        axios.get(`${API}/videos/${videoId}/progress`, getAxiosConfig())
      ]);
      setVideo(videoRes.data);
      setWatchProgress(progressRes.data?.watch_percentage || 0);
      
      // Fetch quiz
      try {
        const quizRes = await axios.get(`${API}/quizzes/${videoId}`, getAxiosConfig());
        setQuiz(quizRes.data);
        setQuizAnswers(new Array(quizRes.data.questions.length).fill(-1));
      } catch (error) {
        console.log('No quiz available for this video');
      }
    } catch (error) {
      console.error('Failed to fetch video data:', error);
      toast.error('Failed to load video');
    } finally {
      setLoading(false);
    }
  };

  const fetchNextVideo = async () => {
    try {
      const response = await axios.get(`${API}/recommendations/next-video`, getAxiosConfig());
      setNextVideo(response.data.video);
    } catch (error) {
      console.error('Failed to fetch next video:', error);
    }
  };

  const updateProgress = async (percentage) => {
    try {
      await axios.post(
        `${API}/videos/${videoId}/progress`,
        {
          watch_percentage: percentage,
          completed: percentage >= 90
        },
        getAxiosConfig()
      );
    } catch (error) {
      console.error('Failed to update progress:', error);
    }
  };

  const handleVideoEnd = () => {
    updateProgress(100);
    if (quiz) {
      setShowQuiz(true);
    } else {
      toast.success('Video completed!');
    }
  };

  const handleQuizSubmit = async (e) => {
    e.preventDefault();
    
    if (quizAnswers.includes(-1)) {
      toast.error('Please answer all questions');
      return;
    }

    try {
      const response = await axios.post(
        `${API}/quizzes/submit`,
        {
          quiz_id: quiz.id,
          answers: quizAnswers
        },
        getAxiosConfig()
      );
      
      setQuizResult(response.data);
      toast.success(`Quiz completed! Score: ${Math.round(response.data.score)}%`);
      
      // Fetch next video recommendation
      fetchNextVideo();
    } catch (error) {
      console.error('Failed to submit quiz:', error);
      toast.error('Failed to submit quiz');
    }
  };

  if (loading) {
    return (
      <div>
        <Navbar />
        <div className="container mx-auto px-4 py-12">
          <div className="animate-pulse space-y-6">
            <div className="aspect-video bg-muted rounded-lg" />
            <div className="h-24 bg-muted rounded-lg" />
          </div>
        </div>
      </div>
    );
  }

  if (!video) {
    return (
      <div>
        <Navbar />
        <div className="container mx-auto px-4 py-12 text-center">
          <p className="text-muted-foreground">Video not found</p>
          <Button onClick={() => navigate('/courses')} className="mt-4">
            Back to Courses
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen" data-testid="video-player-page">
      <Navbar />
      
      <div className="container mx-auto px-4 lg:px-8 py-8 max-w-6xl">
        <Button
          variant="ghost"
          onClick={() => navigate(-1)}
          className="mb-6 gap-2"
          data-testid="back-btn"
        >
          <ArrowLeft className="h-4 w-4" />
          Back
        </Button>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Video Area */}
          <div className="lg:col-span-2 space-y-6">
            {/* Video Player */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <Card className="border-2">
                <CardContent className="p-0">
                  <div className="aspect-video bg-black rounded-t-lg overflow-hidden">
                    <video
                      ref={videoRef}
                      controls
                      onEnded={handleVideoEnd}
                      className="w-full h-full"
                      data-testid="video-player"
                    >
                      <source src={video.url} type="video/mp4" />
                      Your browser does not support the video tag.
                    </video>
                  </div>
                  <div className="p-6">
                    <div className="flex items-center gap-2 mb-3">
                      <Badge>{video.difficulty}</Badge>
                      {video.topics.map((topic, idx) => (
                        <Badge key={idx} variant="outline">
                          {topic}
                        </Badge>
                      ))}
                    </div>
                    <h1 className="text-2xl font-heading font-bold mb-2">{video.title}</h1>
                    <p className="text-muted-foreground mb-4">{video.description}</p>
                    
                    {/* Progress Bar */}
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Watch Progress</span>
                        <span className="font-medium">{Math.round(watchProgress)}%</span>
                      </div>
                      <Progress value={watchProgress} className="h-2" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>

            {/* Quiz Section */}
            {showQuiz && quiz && !quizResult && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
              >
                <Card className="border-2 border-primary/20">
                  <CardHeader>
                    <CardTitle className="font-heading">Complete the Quiz</CardTitle>
                    <CardDescription>
                      Test your understanding of the video content
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <form onSubmit={handleQuizSubmit} className="space-y-6" data-testid="quiz-form">
                      {quiz.questions.map((question, qIdx) => (
                        <div key={qIdx} className="space-y-3">
                          <Label className="text-base font-medium">
                            {qIdx + 1}. {question.question}
                          </Label>
                          <RadioGroup
                            value={quizAnswers[qIdx]?.toString()}
                            onValueChange={(value) => {
                              const newAnswers = [...quizAnswers];
                              newAnswers[qIdx] = parseInt(value);
                              setQuizAnswers(newAnswers);
                            }}
                          >
                            {question.options.map((option, oIdx) => (
                              <div key={oIdx} className="flex items-center space-x-2">
                                <RadioGroupItem
                                  value={oIdx.toString()}
                                  id={`q${qIdx}-o${oIdx}`}
                                  data-testid={`quiz-option-${qIdx}-${oIdx}`}
                                />
                                <Label
                                  htmlFor={`q${qIdx}-o${oIdx}`}
                                  className="font-normal cursor-pointer"
                                >
                                  {option}
                                </Label>
                              </div>
                            ))}
                          </RadioGroup>
                        </div>
                      ))}
                      <Button type="submit" className="w-full" data-testid="submit-quiz-btn">
                        Submit Quiz
                      </Button>
                    </form>
                  </CardContent>
                </Card>
              </motion.div>
            )}

            {/* Quiz Result */}
            {quizResult && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
              >
                <Card
                  className={`border-2 ${
                    quizResult.score >= 70
                      ? 'border-green-500/50 bg-green-500/5'
                      : 'border-yellow-500/50 bg-yellow-500/5'
                  }`}
                  data-testid="quiz-result-card"
                >
                  <CardContent className="p-8 text-center">
                    {quizResult.score >= 70 ? (
                      <CheckCircle2 className="h-16 w-16 text-green-600 mx-auto mb-4" />
                    ) : (
                      <XCircle className="h-16 w-16 text-yellow-600 mx-auto mb-4" />
                    )}
                    <h3 className="text-2xl font-heading font-bold mb-2">
                      {quizResult.score >= 70 ? 'Great Job!' : 'Keep Learning!'}
                    </h3>
                    <p className="text-4xl font-bold text-primary mb-4">
                      {Math.round(quizResult.score)}%
                    </p>
                    <p className="text-muted-foreground mb-6">
                      {quizResult.score >= 70
                        ? 'You have a strong understanding of this topic'
                        : 'Consider reviewing the video for better understanding'}
                    </p>
                    <div className="flex gap-4 justify-center">
                      <Button
                        onClick={() => navigate('/dashboard')}
                        data-testid="back-to-dashboard-btn"
                      >
                        Back to Dashboard
                      </Button>
                      <Button
                        variant="outline"
                        onClick={() => window.location.reload()}
                        data-testid="retake-quiz-btn"
                      >
                        Retake Quiz
                      </Button>
                      
                      {/* Next Video Button */}
                      <Button
                        className="gap-2"
                        onClick={() => {
                          if (nextVideo) {
                            navigate(`/video/${nextVideo.id}`);
                            window.location.reload(); // Force reload to reset state for new video
                          }
                        }}
                        disabled={quizResult.score < 75 || !nextVideo}
                        data-testid="next-video-btn"
                        title={quizResult.score < 75 ? "Score 75% or higher to unlock next video" : "Go to next recommended video"}
                      >
                        Next Video
                        {nextVideo && <span className="text-xs opacity-75 hidden sm:inline">({nextVideo.title})</span>}
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
            >
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg font-heading">Video Info</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Duration</span>
                    <span className="font-medium">{Math.floor(video.duration / 60)} min</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Difficulty</span>
                    <span className="font-medium">{video.difficulty}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground block mb-2">Topics</span>
                    <div className="flex flex-wrap gap-2">
                      {video.topics.map((topic, idx) => (
                        <Badge key={idx} variant="secondary">
                          {topic}
                        </Badge>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>

            {!showQuiz && quiz && (
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.1 }}
              >
                <Card className="border-primary/20">
                  <CardContent className="p-6 text-center">
                    <p className="text-sm text-muted-foreground mb-4">
                      Complete the video to unlock the quiz
                    </p>
                    <Button
                      onClick={() => setShowQuiz(true)}
                      variant="outline"
                      className="w-full"
                      disabled={watchProgress < 90}
                      data-testid="take-quiz-btn"
                    >
                      Take Quiz
                    </Button>
                  </CardContent>
                </Card>
              </motion.div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default VideoPlayerPage;
