import axios from 'axios'

const request = axios.create({
  baseURL: '/api/v1',
  timeout: 120000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
// 响应拦截器
request.interceptors.response.use(
  (response) => {
    const res = response.data as any
    if (res.code !== 0) {
      console.error('API错误:', res.message)
      return Promise.reject(new Error(res.message || '请求失败'))
    }
    return res
  },
  (error) => {
    if (error.code === 'ECONNABORTED') {
      console.error('请求超时')
      return Promise.reject(new Error('请求超时，请稍后重试'))
    }
    if (error.response) {
      const status = error.response.status
      const data = error.response.data
      const message = data?.message || `服务器错误 (${status})`
      console.error(`HTTP ${status}:`, message)
      return Promise.reject(new Error(message))
    }
    console.error('网络错误:', error.message)
    return Promise.reject(new Error('网络连接失败，请检查网络'))
  }
)

export default request