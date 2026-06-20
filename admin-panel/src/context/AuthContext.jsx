import { createContext, useContext, useState, useEffect } from 'react'
import { client } from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const saved = localStorage.getItem('auth')
    if (saved) {
      const { username, password } = JSON.parse(saved)
      client.defaults.auth = { username, password }
      client.get('/api/me')
        .then(() => setUser(username))
        .catch(() => localStorage.removeItem('auth'))
        .finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [])

  const login = async (username, password) => {
    client.defaults.auth = { username, password }
    await client.get('/api/me') // throws if wrong
    localStorage.setItem('auth', JSON.stringify({ username, password }))
    setUser(username)
  }

  const logout = () => {
    localStorage.removeItem('auth')
    client.defaults.auth = undefined
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)