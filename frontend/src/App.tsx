import { useState, useEffect } from 'react'

// ─── Types ────────────────────────────────────────────────────
interface User {
  id: string
  email: string
  full_name: string
  role: string
}

interface Quiz {
  id: string
  title: string
  description: string
  difficulty: string
  status: string
  questions: any[]
  created_at: string
}

interface Room {
  id: string
  room_code: string
  status: string
  quiz_id: string
  created_at: string
}

// ─── API Helper ───────────────────────────────────────────────
const API = 'https://quizforge-backend-as1x.onrender.com/api/v1'

async function apiFetch(path: string, options: any = {}) {
  const token = localStorage.getItem('token')
  const res = await fetch(`${API}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
      ...options.headers
    }
  })
  return res.json()
}

// ─── Login Page ───────────────────────────────────────────────
function LoginPage({ onLogin }: { onLogin: (user: User, token: string) => void }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      const res = await fetch(`${API}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      })
      const data = await res.json()
      if (!res.ok) { setError(data.detail || 'Login failed'); return }
      localStorage.setItem('token', data.access_token)
      onLogin(data.user, data.access_token)
    } catch {
      setError('Cannot connect to server')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '20px' }}>
      <div style={{ background: 'white', borderRadius: '16px', padding: '40px', width: '100%', maxWidth: '420px', boxShadow: '0 20px 60px rgba(0,0,0,0.2)' }}>
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <h1 style={{ fontSize: '28px', fontWeight: 'bold', color: '#4F46E5', margin: 0 }}>🧠 QuizForge AI</h1>
          <p style={{ color: '#6B7280', marginTop: '8px' }}>Sign in to your account</p>
        </div>
        {error && <div style={{ background: '#FEE2E2', color: '#DC2626', padding: '12px', borderRadius: '8px', marginBottom: '16px', fontSize: '14px' }}>{error}</div>}
        <form onSubmit={handleLogin}>
          <div style={{ marginBottom: '16px' }}>
            <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', color: '#374151', marginBottom: '6px' }}>Email</label>
            <input type="email" value={email} onChange={e => setEmail(e.target.value)} required style={{ width: '100%', padding: '12px 16px', border: '1px solid #D1D5DB', borderRadius: '8px', fontSize: '16px', outline: 'none', boxSizing: 'border-box' }} placeholder="nisha@example.com" />
          </div>
          <div style={{ marginBottom: '24px' }}>
            <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', color: '#374151', marginBottom: '6px' }}>Password</label>
            <input type="password" value={password} onChange={e => setPassword(e.target.value)} required style={{ width: '100%', padding: '12px 16px', border: '1px solid #D1D5DB', borderRadius: '8px', fontSize: '16px', outline: 'none', boxSizing: 'border-box' }} placeholder="••••••••" />
          </div>
          <button type="submit" disabled={loading} style={{ width: '100%', padding: '14px', background: loading ? '#9CA3AF' : '#4F46E5', color: 'white', border: 'none', borderRadius: '8px', fontSize: '16px', fontWeight: '600', cursor: loading ? 'not-allowed' : 'pointer' }}>
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>
      </div>
    </div>
  )
}

// ─── Dashboard Page ───────────────────────────────────────────
function Dashboard({ user, onLogout }: { user: User, onLogout: () => void }) {
  const [quizzes, setQuizzes] = useState<Quiz[]>([])
  const [rooms, setRooms] = useState<Room[]>([])
  const [view, setView] = useState<'quizzes' | 'create' | 'room'>('quizzes')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')

  // Create Quiz Form
  const [quizTitle, setQuizTitle] = useState('')
  const [quizDesc, setQuizDesc] = useState('')
  const [questions, setQuestions] = useState([
    { question_text: '', options: { A: '', B: '', C: '', D: '' }, correct_answer: 'A', explanation: '', difficulty: 'medium', order_index: 1, points: 100 }
  ])

  // Room Form
  const [selectedQuizId, setSelectedQuizId] = useState('')
  const [activeRoom, setActiveRoom] = useState<Room | null>(null)

  useEffect(() => {
    loadQuizzes()
  }, [])

  const loadQuizzes = async () => {
    const data = await apiFetch('/quizzes')
    if (Array.isArray(data)) setQuizzes(data)
  }

  const createQuiz = async () => {
    if (!quizTitle) { setMessage('Title required'); return }
    setLoading(true)
    try {
      const data = await apiFetch('/quizzes', {
        method: 'POST',
        body: JSON.stringify({
          title: quizTitle,
          description: quizDesc,
          difficulty: 'medium',
          is_public: true,
          time_limit: 30,
          questions: questions.filter(q => q.question_text)
        })
      })
      if (data.id) {
        setMessage('✅ Quiz created successfully!')
        setQuizTitle('')
        setQuizDesc('')
        setQuestions([{ question_text: '', options: { A: '', B: '', C: '', D: '' }, correct_answer: 'A', explanation: '', difficulty: 'medium', order_index: 1, points: 100 }])
        loadQuizzes()
        setView('quizzes')
      }
    } catch { setMessage('Failed to create quiz') }
    finally { setLoading(false) }
  }

  const createRoom = async () => {
    if (!selectedQuizId) { setMessage('Select a quiz first'); return }
    setLoading(true)
    try {
      const room = await apiFetch('/rooms', {
        method: 'POST',
        body: JSON.stringify({ quiz_id: selectedQuizId, max_participants: 30, is_team_mode: false })
      })
      if (room.room_code) {
        setActiveRoom(room)
        setRooms([room, ...rooms])
        setMessage(`✅ Room created! Code: ${room.room_code}`)
      }
    } catch { setMessage('Failed to create room') }
    finally { setLoading(false) }
  }

  const startRoom = async (roomCode: string) => {
  try {
    const data = await apiFetch(`/rooms/${roomCode}/start`, { method: 'POST' })
    if (data.status === 'active') {
      setMessage(`✅ Room ${roomCode} is now ACTIVE! Share code with students.`)
      setActiveRoom(data)
    } else if (data.detail) {
      setMessage(`❌ Error: ${data.detail}`)
    } else {
      setMessage(`✅ Room started! Status: ${data.status}`)
    }
  } catch (err) {
    setMessage('❌ Failed to start room. Make sure backend is running.')
  }
}


  const updateQuestion = (idx: number, field: string, value: string) => {
    const updated = [...questions]
    if (field.startsWith('opt_')) {
      const optKey = field.replace('opt_', '')
      updated[idx] = { ...updated[idx], options: { ...updated[idx].options, [optKey]: value } }
    } else {
      updated[idx] = { ...updated[idx], [field]: value }
    }
    setQuestions(updated)
  }

  const addQuestion = () => {
    setQuestions([...questions, {
      question_text: '', options: { A: '', B: '', C: '', D: '' },
      correct_answer: 'A', explanation: '', difficulty: 'medium',
      order_index: questions.length + 1, points: 100
    }])
  }

  return (
    <div style={{ minHeight: '100vh', background: '#F8FAFC' }}>

      {/* Navbar */}
      <nav style={{ background: '#4F46E5', padding: '16px 32px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1 style={{ color: 'white', margin: 0, fontSize: '20px', fontWeight: 'bold' }}>🧠 QuizForge AI</h1>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <span style={{ color: '#C7D2FE', fontSize: '14px' }}>👤 {user.full_name}</span>
          <button onClick={onLogout} style={{ background: 'rgba(255,255,255,0.2)', color: 'white', border: '1px solid rgba(255,255,255,0.3)', padding: '8px 16px', borderRadius: '8px', cursor: 'pointer', fontSize: '14px' }}>
            Logout
          </button>
        </div>
      </nav>

      <div style={{ maxWidth: '1000px', margin: '0 auto', padding: '32px 20px' }}>

        {/* Tabs */}
        <div style={{ display: 'flex', gap: '12px', marginBottom: '32px' }}>
          {[
            { key: 'quizzes', label: '📚 My Quizzes' },
            { key: 'create', label: '➕ Create Quiz' },
            { key: 'room', label: '🎮 Create Room' }
          ].map(tab => (
            <button
              key={tab.key}
              onClick={() => { setView(tab.key as any); setMessage('') }}
              style={{
                padding: '10px 20px',
                background: view === tab.key ? '#4F46E5' : 'white',
                color: view === tab.key ? 'white' : '#374151',
                border: '1px solid #E5E7EB',
                borderRadius: '8px',
                cursor: 'pointer',
                fontWeight: '500',
                fontSize: '14px'
              }}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Message */}
        {message && (
          <div style={{ background: message.includes('✅') ? '#D1FAE5' : '#FEE2E2', color: message.includes('✅') ? '#065F46' : '#DC2626', padding: '12px 16px', borderRadius: '8px', marginBottom: '20px', fontSize: '14px' }}>
            {message}
          </div>
        )}

        {/* ── My Quizzes View ── */}
        {view === 'quizzes' && (
          <div>
            <h2 style={{ fontSize: '20px', fontWeight: '600', color: '#1F2937', marginBottom: '16px' }}>My Quizzes</h2>
            {quizzes.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '60px', background: 'white', borderRadius: '12px', border: '1px solid #E5E7EB' }}>
                <p style={{ fontSize: '48px', margin: '0 0 16px' }}>📝</p>
                <p style={{ color: '#6B7280' }}>No quizzes yet. Create your first quiz!</p>
                <button onClick={() => setView('create')} style={{ marginTop: '16px', padding: '10px 24px', background: '#4F46E5', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer' }}>
                  Create Quiz
                </button>
              </div>
            ) : (
              <div style={{ display: 'grid', gap: '16px' }}>
                {quizzes.map(quiz => (
                  <div key={quiz.id} style={{ background: 'white', borderRadius: '12px', padding: '20px', border: '1px solid #E5E7EB', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <h3 style={{ margin: '0 0 4px', fontSize: '16px', fontWeight: '600', color: '#1F2937' }}>{quiz.title}</h3>
                      <p style={{ margin: 0, fontSize: '13px', color: '#6B7280' }}>
                        {quiz.questions?.length || 0} questions • {quiz.difficulty} • {quiz.status}
                      </p>
                    </div>
                    <div style={{ display: 'flex', gap: '8px' }}>
                      <button
                        onClick={() => { setSelectedQuizId(quiz.id); setView('room') }}
                        style={{ padding: '8px 16px', background: '#4F46E5', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', fontSize: '13px' }}
                      >
                        🎮 Start Room
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* ── Create Quiz View ── */}
        {view === 'create' && (
          <div style={{ background: 'white', borderRadius: '12px', padding: '24px', border: '1px solid #E5E7EB' }}>
            <h2 style={{ fontSize: '20px', fontWeight: '600', color: '#1F2937', marginBottom: '20px' }}>Create New Quiz</h2>

            <div style={{ marginBottom: '16px' }}>
              <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', color: '#374151', marginBottom: '6px' }}>Quiz Title *</label>
              <input value={quizTitle} onChange={e => setQuizTitle(e.target.value)} style={{ width: '100%', padding: '10px 14px', border: '1px solid #D1D5DB', borderRadius: '8px', fontSize: '15px', boxSizing: 'border-box' }} placeholder="e.g. Python Basics Quiz" />
            </div>

            <div style={{ marginBottom: '24px' }}>
              <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', color: '#374151', marginBottom: '6px' }}>Description</label>
              <input value={quizDesc} onChange={e => setQuizDesc(e.target.value)} style={{ width: '100%', padding: '10px 14px', border: '1px solid #D1D5DB', borderRadius: '8px', fontSize: '15px', boxSizing: 'border-box' }} placeholder="Brief description..." />
            </div>

            <h3 style={{ fontSize: '16px', fontWeight: '600', color: '#1F2937', marginBottom: '16px' }}>Questions</h3>

            {questions.map((q, idx) => (
              <div key={idx} style={{ background: '#F9FAFB', borderRadius: '10px', padding: '16px', marginBottom: '16px', border: '1px solid #E5E7EB' }}>
                <p style={{ fontWeight: '600', color: '#4F46E5', margin: '0 0 12px' }}>Question {idx + 1}</p>

                <input
                  value={q.question_text}
                  onChange={e => updateQuestion(idx, 'question_text', e.target.value)}
                  style={{ width: '100%', padding: '10px 14px', border: '1px solid #D1D5DB', borderRadius: '8px', fontSize: '14px', marginBottom: '12px', boxSizing: 'border-box' }}
                  placeholder="Enter your question..."
                />

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginBottom: '12px' }}>
                  {(['A', 'B', 'C', 'D'] as const).map(opt => (
                    <input
                      key={opt}
                      value={q.options[opt]}
                      onChange={e => updateQuestion(idx, `opt_${opt}`, e.target.value)}
                      style={{ padding: '8px 12px', border: '1px solid #D1D5DB', borderRadius: '6px', fontSize: '14px' }}
                      placeholder={`Option ${opt}`}
                    />
                  ))}
                </div>

                <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                  <label style={{ fontSize: '13px', color: '#374151' }}>Correct Answer:</label>
                  <select value={q.correct_answer} onChange={e => updateQuestion(idx, 'correct_answer', e.target.value)} style={{ padding: '6px 10px', border: '1px solid #D1D5DB', borderRadius: '6px', fontSize: '14px' }}>
                    <option value="A">A</option>
                    <option value="B">B</option>
                    <option value="C">C</option>
                    <option value="D">D</option>
                  </select>
                </div>
              </div>
            ))}

            <div style={{ display: 'flex', gap: '12px' }}>
              <button onClick={addQuestion} style={{ padding: '10px 20px', background: 'white', color: '#4F46E5', border: '1px solid #4F46E5', borderRadius: '8px', cursor: 'pointer', fontSize: '14px' }}>
                + Add Question
              </button>
              <button onClick={createQuiz} disabled={loading} style={{ padding: '10px 24px', background: loading ? '#9CA3AF' : '#4F46E5', color: 'white', border: 'none', borderRadius: '8px', cursor: loading ? 'not-allowed' : 'pointer', fontSize: '14px', fontWeight: '600' }}>
                {loading ? 'Creating...' : '✓ Create Quiz'}
              </button>
            </div>
          </div>
        )}

        {/* ── Create Room View ── */}
        {view === 'room' && (
          <div style={{ background: 'white', borderRadius: '12px', padding: '24px', border: '1px solid #E5E7EB' }}>
            <h2 style={{ fontSize: '20px', fontWeight: '600', color: '#1F2937', marginBottom: '20px' }}>🎮 Create Quiz Room</h2>

            <div style={{ marginBottom: '20px' }}>
              <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', color: '#374151', marginBottom: '8px' }}>Select Quiz</label>
              <select
                value={selectedQuizId}
                onChange={e => setSelectedQuizId(e.target.value)}
                style={{ width: '100%', padding: '12px 14px', border: '1px solid #D1D5DB', borderRadius: '8px', fontSize: '15px' }}
              >
                <option value="">-- Choose a quiz --</option>
                {quizzes.map(q => (
                  <option key={q.id} value={q.id}>{q.title}</option>
                ))}
              </select>
            </div>

            <button onClick={createRoom} disabled={loading} style={{ padding: '12px 28px', background: loading ? '#9CA3AF' : '#4F46E5', color: 'white', border: 'none', borderRadius: '8px', cursor: loading ? 'not-allowed' : 'pointer', fontSize: '15px', fontWeight: '600' }}>
              {loading ? 'Creating...' : '🚀 Create Room'}
            </button>

            {activeRoom && (
              <div style={{ marginTop: '24px', background: '#EEF2FF', borderRadius: '12px', padding: '20px', border: '1px solid #C7D2FE' }}>
                <h3 style={{ color: '#4F46E5', margin: '0 0 12px' }}>Room Created! 🎉</h3>
                <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#1F2937', letterSpacing: '4px', marginBottom: '12px' }}>
                  {activeRoom.room_code}
                </div>
                <p style={{ color: '#6B7280', fontSize: '13px', marginBottom: '16px' }}>Share this code with participants</p>
                <button
                  onClick={() => startRoom(activeRoom.room_code)}
                  style={{ padding: '10px 24px', background: '#10B981', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', fontSize: '14px', fontWeight: '600' }}
                >
                  ▶ Start Quiz
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
// ─── Join Page (Student) ──────────────────────────────────────
function JoinPage({ onJoined }: { onJoined: (roomCode: string, nickname: string) => void }) {
  const [roomCode, setRoomCode] = useState('')
  const [nickname, setNickname] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleJoin = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const res = await fetch(`${API}/rooms/${roomCode.toUpperCase()}/join`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nickname })
      })
      const data = await res.json()

      if (!res.ok) {
        setError(data.detail || 'Failed to join room')
        return
      }

      onJoined(roomCode.toUpperCase(), nickname)

    } catch {
      setError('Cannot connect to server')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '20px' }}>
      <div style={{ background: 'white', borderRadius: '16px', padding: '40px', width: '100%', maxWidth: '420px', boxShadow: '0 20px 60px rgba(0,0,0,0.2)' }}>
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <h1 style={{ fontSize: '28px', fontWeight: 'bold', color: '#4F46E5', margin: 0 }}>🧠 QuizForge AI</h1>
          <p style={{ color: '#6B7280', marginTop: '8px' }}>Join a Quiz Room</p>
        </div>

        {error && (
          <div style={{ background: '#FEE2E2', color: '#DC2626', padding: '12px', borderRadius: '8px', marginBottom: '16px', fontSize: '14px' }}>
            {error}
          </div>
        )}

        <form onSubmit={handleJoin}>
          <div style={{ marginBottom: '16px' }}>
            <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', color: '#374151', marginBottom: '6px' }}>Room Code</label>
            <input
              type="text"
              value={roomCode}
              onChange={e => setRoomCode(e.target.value.toUpperCase())}
              required
              maxLength={6}
              style={{ width: '100%', padding: '12px 16px', border: '1px solid #D1D5DB', borderRadius: '8px', fontSize: '24px', fontWeight: 'bold', letterSpacing: '6px', textAlign: 'center', outline: 'none', boxSizing: 'border-box' }}
              placeholder="ABC123"
            />
          </div>

          <div style={{ marginBottom: '24px' }}>
            <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', color: '#374151', marginBottom: '6px' }}>Your Nickname</label>
            <input
              type="text"
              value={nickname}
              onChange={e => setNickname(e.target.value)}
              required
              style={{ width: '100%', padding: '12px 16px', border: '1px solid #D1D5DB', borderRadius: '8px', fontSize: '16px', outline: 'none', boxSizing: 'border-box' }}
              placeholder="Enter your name"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            style={{ width: '100%', padding: '14px', background: loading ? '#9CA3AF' : '#4F46E5', color: 'white', border: 'none', borderRadius: '8px', fontSize: '16px', fontWeight: '600', cursor: loading ? 'not-allowed' : 'pointer' }}
          >
            {loading ? 'Joining...' : '🚀 Join Quiz'}
          </button>
        </form>
      </div>
    </div>
  )
}

// ─── Live Quiz Page ───────────────────────────────────────────
function LiveQuizPage({ roomCode, nickname }: { roomCode: string, nickname: string }) {
  const [messages, setMessages] = useState<string[]>([])
  const [leaderboard, setLeaderboard] = useState<any[]>([])
  const [connected, setConnected] = useState(false)
  const [ws, setWs] = useState<WebSocket | null>(null)
  const [answered, setAnswered] = useState(false)
  const [lastResult, setLastResult] = useState<any>(null)

  useEffect(() => {
    const socket = new WebSocket(
      `wss://quizforge-backend-as1x.onrender.com/ws/room/${roomCode}?nickname=${nickname}`
)
    

    socket.onopen = () => {
      setConnected(true)
      addMessage('✅ Connected to room!')
    }

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data)

      if (data.type === 'leaderboard_update') {
        setLeaderboard(data.entries)
      } else if (data.type === 'answer_result') {
        setLastResult(data)
        addMessage(`${data.correct ? '✅ Correct!' : '❌ Wrong!'} +${data.points_earned} points`)
      } else if (data.type === 'player_joined') {
        addMessage(`👤 ${data.nickname} joined! (${data.player_count} players)`)
      } else if (data.type === 'player_left') {
        addMessage(`👋 ${data.nickname} left`)
      } else {
        addMessage(`📨 ${data.type}: ${JSON.stringify(data).substring(0, 80)}`)
      }
    }

    socket.onclose = () => {
      setConnected(false)
      addMessage('❌ Disconnected')
    }

    setWs(socket)
    return () => socket.close()
  }, [])

  const addMessage = (msg: string) => {
    setMessages(prev => [`${new Date().toLocaleTimeString()} — ${msg}`, ...prev].slice(0, 20))
  }

  const submitAnswer = (answer: string) => {
    if (!ws || answered) return
    ws.send(JSON.stringify({
      type: 'submit_answer',
      question_index: 0,
      answer,
      time_taken: 5
    }))
    setAnswered(true)
  }

  return (
    <div style={{ minHeight: '100vh', background: '#F8FAFC' }}>
      <nav style={{ background: '#4F46E5', padding: '16px 32px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1 style={{ color: 'white', margin: 0, fontSize: '20px' }}>🧠 QuizForge AI</h1>
        <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
          <span style={{ color: '#C7D2FE', fontSize: '14px' }}>Room: <strong style={{ color: 'white', letterSpacing: '2px' }}>{roomCode}</strong></span>
          <span style={{ color: '#C7D2FE', fontSize: '14px' }}>👤 {nickname}</span>
          <span style={{ padding: '4px 12px', borderRadius: '20px', fontSize: '12px', background: connected ? '#10B981' : '#EF4444', color: 'white' }}>
            {connected ? '● Live' : '● Offline'}
          </span>
        </div>
      </nav>

      <div style={{ maxWidth: '1000px', margin: '0 auto', padding: '24px 20px', display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '24px' }}>

        {/* Left — Quiz Area */}
        <div>
          {/* Answer Buttons */}
          <div style={{ background: 'white', borderRadius: '12px', padding: '24px', border: '1px solid #E5E7EB', marginBottom: '20px' }}>
            <h2 style={{ fontSize: '18px', fontWeight: '600', color: '#1F2937', marginBottom: '8px' }}>Submit Answer</h2>
            <p style={{ color: '#6B7280', fontSize: '14px', marginBottom: '16px' }}>
              {answered ? '✅ Answer submitted! Wait for next question.' : 'Click to submit your answer:'}
            </p>

            {lastResult && (
              <div style={{ background: lastResult.correct ? '#D1FAE5' : '#FEE2E2', padding: '12px', borderRadius: '8px', marginBottom: '16px', fontSize: '14px', color: lastResult.correct ? '#065F46' : '#DC2626' }}>
                {lastResult.correct ? '✅ Correct!' : '❌ Wrong!'} Points earned: {lastResult.points_earned} | Total: {lastResult.total_score}
                {lastResult.explanation && <p style={{ marginTop: '8px', color: '#374151' }}>💡 {lastResult.explanation}</p>}
              </div>
            )}

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
              {['A', 'B', 'C', 'D'].map(opt => (
                <button
                  key={opt}
                  onClick={() => submitAnswer(opt)}
                  disabled={answered}
                  style={{
                    padding: '16px',
                    background: answered ? '#F3F4F6' : '#4F46E5',
                    color: answered ? '#9CA3AF' : 'white',
                    border: 'none',
                    borderRadius: '10px',
                    fontSize: '18px',
                    fontWeight: 'bold',
                    cursor: answered ? 'not-allowed' : 'pointer'
                  }}
                >
                  {opt}
                </button>
              ))}
            </div>

            {answered && (
              <button
                onClick={() => { setAnswered(false); setLastResult(null) }}
                style={{ marginTop: '12px', padding: '8px 16px', background: '#6366F1', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', fontSize: '13px' }}
              >
                Next Question
              </button>
            )}
          </div>

          {/* Messages */}
          <div style={{ background: 'white', borderRadius: '12px', padding: '20px', border: '1px solid #E5E7EB' }}>
            <h3 style={{ fontSize: '16px', fontWeight: '600', color: '#1F2937', marginBottom: '12px' }}>Live Feed</h3>
            <div style={{ maxHeight: '200px', overflowY: 'auto' }}>
              {messages.map((msg, i) => (
                <p key={i} style={{ margin: '4px 0', fontSize: '13px', color: '#6B7280', padding: '4px 8px', background: '#F9FAFB', borderRadius: '4px' }}>{msg}</p>
              ))}
            </div>
          </div>
        </div>

        {/* Right — Leaderboard */}
        <div style={{ background: 'white', borderRadius: '12px', padding: '20px', border: '1px solid #E5E7EB', height: 'fit-content' }}>
          <h3 style={{ fontSize: '16px', fontWeight: '600', color: '#1F2937', marginBottom: '16px' }}>🏆 Leaderboard</h3>
          {leaderboard.length === 0 ? (
            <p style={{ color: '#9CA3AF', fontSize: '14px', textAlign: 'center' }}>Waiting for scores...</p>
          ) : (
            leaderboard.map((entry, i) => (
              <div key={i} style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                padding: '10px 12px',
                marginBottom: '8px',
                borderRadius: '8px',
                background: i === 0 ? '#FEF3C7' : '#F9FAFB',
                border: i === 0 ? '1px solid #FCD34D' : '1px solid #F3F4F6'
              }}>
                <span style={{ fontSize: '14px', fontWeight: i === 0 ? 'bold' : 'normal' }}>
                  {i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : `${i + 1}.`} {entry.nickname}
                </span>
                <span style={{ fontSize: '14px', fontWeight: '600', color: '#4F46E5' }}>{entry.score} pts</span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}

// ─── Main App ─────────────────────────────────────────────────
export default function App() {
  const [user, setUser] = useState<User | null>(() => {
    const saved = localStorage.getItem('user')
    return saved ? JSON.parse(saved) : null
  })
  const [page, setPage] = useState<'login' | 'join' | 'live'>('login')
  const [roomCode, setRoomCode] = useState('')
  const [nickname, setNickname] = useState('')

  const handleLogin = (user: User) => {
    localStorage.setItem('user', JSON.stringify(user))
    setUser(user)
  }

  const handleLogout = () => {
    localStorage.clear()
    setUser(null)
    setPage('login')
  }

  const handleJoined = (code: string, nick: string) => {
    setRoomCode(code)
    setNickname(nick)
    setPage('live')
  }

  if (user) return <Dashboard user={user} onLogout={handleLogout} />
  if (page === 'join') return <JoinPage onJoined={handleJoined} />
  if (page === 'live') return <LiveQuizPage roomCode={roomCode} nickname={nickname} />

  return (
    <div style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '20px' }}>
      <div style={{ background: 'white', borderRadius: '16px', padding: '40px', width: '100%', maxWidth: '420px', boxShadow: '0 20px 60px rgba(0,0,0,0.2)', textAlign: 'center' }}>
        <h1 style={{ fontSize: '32px', fontWeight: 'bold', color: '#4F46E5', margin: '0 0 8px' }}>🧠 QuizForge AI</h1>
        <p style={{ color: '#6B7280', marginBottom: '32px' }}>AI-powered real-time quiz platform</p>

        <button
          onClick={() => setPage('login')}
          style={{ width: '100%', padding: '14px', background: '#4F46E5', color: 'white', border: 'none', borderRadius: '8px', fontSize: '16px', fontWeight: '600', cursor: 'pointer', marginBottom: '12px' }}
        >
          🎓 Login as Teacher
        </button>

        <button
          onClick={() => setPage('join')}
          style={{ width: '100%', padding: '14px', background: 'white', color: '#4F46E5', border: '2px solid #4F46E5', borderRadius: '8px', fontSize: '16px', fontWeight: '600', cursor: 'pointer' }}
        >
          🎮 Join as Student
        </button>
      </div>
    </div>
  )
}