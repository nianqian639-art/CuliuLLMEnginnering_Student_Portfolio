import chess
import os
import requests
import json
from dotenv import load_dotenv
from log_config import logger

# 加载环境变量
load_dotenv()

# 千问API配置
API_KEY = os.getenv("QIANWEN_API_KEY")
SECRET_KEY = os.getenv("QIANWEN_SECRET_KEY")
ENDPOINT = os.getenv("QIANWEN_ENDPOINT")
MODEL_NAME = os.getenv("MODEL_NAME")

class ChessLLMGuide:
    def __init__(self):
        self.board = chess.Board()  # 初始化空棋盘
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"  # 通义千帆鉴权格式
        }

    def _call_qianwen(self, prompt: str, temperature: float = 0.7) -> str:
        """
        核心函数：调用千问API，处理国际象棋相关提示词
        :param prompt: 输入提示词
        :param temperature: 随机性（0=确定性，1=随机性高）
        :return: 千问返回的回答
        """
        # 构造OpenAI兼容格式的请求体
        payload = {
            "model": MODEL_NAME,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": 2000  # 最大返回长度
        }

        try:
            logger.info(f"调用千问API，Prompt: {prompt[:50]}...")
            response = requests.post(
                ENDPOINT,
                headers=self.headers,
                data=json.dumps(payload),
                timeout=30
            )
            response.raise_for_status()  # 抛出HTTP错误
            result = response.json()
            answer = result["choices"][0]["message"]["content"]
            logger.info(f"千问API返回成功，回答长度: {len(answer)}")
            return answer
        except Exception as e:
            logger.error(f"千问API调用失败: {str(e)}", exc_info=True)
            return f"API调用失败: {str(e)}"

    def explain_rule(self, topic: str = "基础规则") -> str:
        """
        功能1：调用千问讲解国际象棋规则（可指定主题）
        :param topic: 规则主题（如"兵的走法"、"王车易位"、"将死条件"）
        :return: 规则讲解内容
        """
        prompt = f"""
        请以通俗易懂的方式讲解国际象棋的「{topic}」，要求：
        1. 分点说明，适合新手理解；
        2. 举例说明关键规则（如兵的升变举例）；
        3. 指出新手常见错误（如误判王车易位条件）。
        """
        return self._call_qianwen(prompt)

    def suggest_move(self) -> str:
        """
        功能2：基于当前棋局，调用千问给出走法建议（结合棋局逻辑）
        :return: 走法建议 + 分析
        """
        # 获取当前棋局的FEN格式（国际象棋标准棋局表示）
        fen = self.board.fen()
        # 检查当前棋局是否合法
        if not self.board.is_valid():
            logger.warning(f"无效棋局，FEN: {fen}")
            return "当前棋局无效，请检查走法！"
        
        prompt = f"""
        你是国际象棋资深教练，分析以下棋局并给出走法建议：
        1. 棋局FEN格式：{fen}
        2. 首先说明当前局势（优势方、关键棋子位置、潜在威胁）；
        3. 给出3个可选走法（用代数记法，如e4、Nf3），并分析每个走法的优劣；
        4. 优先推荐1个最优走法，并解释原因；
        5. 指出新手可能犯的错误走法（如果有）。
        """
        return self._call_qianwen(prompt, temperature=0.6)  # 走法建议降低随机性

    def analyze_mistake(self, move_sequence: str) -> str:
        """
        功能3：复盘走法序列，调用千问分析错误走法
        :param move_sequence: 走法序列（如"e4 e5 Nf3 Nc6 Bc4 Bc5"）
        :return: 错误分析 + 改进建议
        """
        # 验证走法序列并加载到棋盘
        try:
            self.board.reset()
            moves = move_sequence.split()
            for move in moves:
                self.board.push_san(move)  # 按代数记法走棋
            logger.info(f"成功加载复盘走法: {move_sequence}")
        except Exception as e:
            logger.error(f"走法序列无效: {str(e)}", exc_info=True)
            return f"走法序列无效: {str(e)}（请使用代数记法，如e4 e5）"
        
        prompt = f"""
        请复盘以下国际象棋走法序列并分析错误：
        1. 走法序列：{move_sequence}
        2. 逐步分析每个走法的合理性；
        3. 指出其中的错误走法（如送子、暴露王、错失进攻机会）；
        4. 针对错误给出具体改进建议；
        5. 总结本次对局的核心问题和提升方向。
        """
        return self._call_qianwen(prompt, temperature=0.5)

    def reset_board(self):
        """重置棋盘"""
        self.board.reset()
        logger.info("棋盘已重置")

    def make_move(self, move: str) -> bool:
        """
        执行走法（验证合法性）
        :param move: 代数记法走法（如e4）
        :return: 走法是否合法
        """
        try:
            self.board.push_san(move)
            logger.info(f"执行走法成功: {move}，当前棋局FEN: {self.board.fen()}")
            return True
        except Exception as e:
            logger.error(f"走法执行失败: {move}，错误: {str(e)}")
            return False
