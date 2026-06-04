import request from './request'

export interface LoginParams {
  username: string
  password: string
}

export interface UserInfo {
  id: string
  username: string
}

export interface LoginResult {
  access_token: string
  token_type: string
  user: UserInfo
}

// 登录
export function login(params: LoginParams): Promise<LoginResult> {
  return request.post('/auth/login', params).then((res: any) => res.data)
}

// 获取当前用户信息
export function getCurrentUser(): Promise<UserInfo> {
  return request.get('/auth/me').then((res: any) => res.data)
}
