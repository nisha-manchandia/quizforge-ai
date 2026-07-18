export interface User {
  id: string
  email: string
  full_name: string
  role: string
  is_active: boolean
  is_guest: boolean
  created_at: string
}

export interface Question {
  id: string
  quiz_id: string
  question_text: string
  options: Record<string, string>
  correct_answer: string
  explanation: string
  difficulty: string
  order_index: number
  points: number
}

export interface Quiz {
  id: string
  title: string
  description: string
  creator_id: string
  difficulty: string
  is_public: boolean
  time_limit: number
  status: string
  generation_source: string
  questions: Question[]
  created_at: string
}

export interface Room {
  id: string
  quiz_id: string
  host_id: string
  room_code: string
  status: string
  current_question: number
  max_participants: number
  created_at: string
}

export interface LeaderboardEntry {
  rank: number
  nickname: string
  score: number
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: User
}