"""
Prompt 智能助手 API 路由

提供 AI 驱动的提示词优化/扩写/翻译功能，帮助用户生成更高质量的图片提示词。
"""
import logging
import httpx
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1 import success_response
from app.api.deps import require_auth
from app.models import get_db
from app.schemas.prompt import PromptOptimizeRequest, PromptOptimizeResponse
from app.services.ai_model_config_service import ai_model_config_service
from app.services.ai_client import ai_client
from app.core.exceptions import AppException

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/prompts", tags=["Prompt智能助手"])

# 不同操作类型对应的系统提示词
SYSTEM_PROMPTS = {
    "optimize": """你是一位专业的 AI 图片生成提示词工程师。你的任务是将用户简单的提示词优化为更详细、更专业的图片生成提示词。

优化规则：
1. 补充画面细节：光照、构图、色彩、材质、氛围
2. 添加质量关键词：如 "high quality", "4k", "detailed", "sharp focus"
3. 明确主体和背景关系
4. 保持用户的原始意图和风格方向
5. 如果用户指定了风格，围绕该风格进行优化

输出要求：只输出优化后的英文提示词，不要包含任何解释或额外文字。提示词长度控制在150词以内。""",

    "expand": """你是一位创意图片生成提示词专家。你的任务是将用户简短的提示词大幅扩写为丰富详细的场景描述。

扩写规则：
1. 展开场景叙事：时间、地点、人物、动作、情绪
2. 添加丰富的视觉细节：纹理、光影、色彩搭配、透视
3. 融入艺术参考：摄影/绘画风格、镜头类型、焦段
4. 加入氛围和环境描述
5. 保持所有细节协调一致，不矛盾

输出要求：只输出扩写后的英文提示词，不要包含任何解释或额外文字。提示词长度控制在80-120词。""",

    "translate": """你是一位专业的翻译助手。请将用户的中文提示词翻译为适合 AI 图片生成的英文提示词。

翻译规则：
1. 使用地道的英文表达，避免中式英语
2. 保留所有视觉描述细节
3. 将中文成语、诗词意境转化为具体的视觉描述
4. 确保生成的英文提示词可以直接用于 AI 图片生成

输出要求：只输出翻译后的英文提示词，不要包含任何解释或额外文字。""",
}


@router.post("/optimize", dependencies=[Depends(require_auth)])
async def optimize_prompt(request: PromptOptimizeRequest, db: Session = Depends(get_db)):
    """AI 优化提示词

    根据配置的 AI 模型对用户输入的提示词进行智能优化/扩写/翻译，
    返回可直接用于图片生成的高质量提示词。
    """
    # 1. 获取激活的 AI 模型配置
    config = ai_model_config_service.get_active(db)
    if not config:
        raise AppException(
            code=11001,
            message="未找到激活的 AI 模型配置，请先在「设置」页面配置并激活一个 AI 模型",
            status_code=400,
        )

    # 2. 选择系统提示词
    action = request.action or "optimize"
    system_prompt = SYSTEM_PROMPTS.get(action, SYSTEM_PROMPTS["optimize"])

    # 3. 构建用户消息
    user_content = f"原始提示词：{request.prompt}"
    if request.style:
        user_content += f"\n期望风格：{request.style}"

    # 4. 调用 AI 模型
    try:
        result = await ai_client.chat_completion(
            api_base_url=config.api_base_url,
            api_key=config.api_key,
            model=config.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            temperature=config.temperature or 0.7,
            max_tokens=config.max_tokens or 1024,
        )
    except httpx.TimeoutException:
        logger.error("AI 优化提示词超时")
        raise AppException(code=11002, message="AI 模型响应超时，请稍后重试", status_code=502)
    except httpx.HTTPStatusError as e:
        logger.error(f"AI API 返回错误: status={e.response.status_code}")
        raise AppException(code=11002, message=f"AI 模型服务异常 (HTTP {e.response.status_code})", status_code=502)
    except httpx.RequestError as e:
        logger.error(f"AI API 网络错误: {str(e)}")
        raise AppException(code=11002, message="AI 模型网络连接失败，请检查配置", status_code=502)
    except Exception as e:
        logger.error(f"AI 优化提示词失败: {type(e).__name__}: {str(e)}")
        raise AppException(code=11002, message="AI 模型调用失败，请稍后重试", status_code=500)

    # 5. 提取优化后的文本
    choices = result.get("choices", [])
    if not choices:
        raise AppException(code=11003, message="AI 模型返回了空结果", status_code=500)

    optimized_text = choices[0].get("message", {}).get("content", "").strip()
    if not optimized_text:
        raise AppException(code=11004, message="AI 优化结果为空", status_code=500)

    logger.info(f"Prompt 优化完成: action={action}, 原始长度={len(request.prompt)}, 优化后长度={len(optimized_text)}")

    response_data = PromptOptimizeResponse(
        original_prompt=request.prompt,
        optimized_prompt=optimized_text,
        action=action,
    )
    return success_response(data=response_data.model_dump(), message="提示词优化成功")
