import request from './request'

export interface Text2ImgParams {
  prompt: string
  negative_prompt?: string
  image_size: string
  style?: string
  cfg_scale: number
  seed: number
  image_count: number
}

export interface Img2ImgParams extends Text2ImgParams {
  reference_image_path: string
}

export interface InpaintingParams extends Text2ImgParams {
  reference_image_path: string
  mask_image_path: string
}

export async function submitText2Img(params: Text2ImgParams) {
  return request.post('/generations/text2img', params)
}

export async function submitImg2Img(params: Img2ImgParams) {
  return request.post('/generations/img2img', params)
}

export async function submitInpainting(params: InpaintingParams) {
  return request.post('/generations/inpainting', params)
}

export async function queryStatus(generationId: string) {
  return request.get(`/generations/${generationId}/status`)
}

export async function getResult(generationId: string) {
  return request.get(`/generations/${generationId}`)
}