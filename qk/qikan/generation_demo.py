# -*- coding: utf-8 -*-
import os
import re
from docxtpl import DocxTemplate
import subprocess # 用于执行外部命令
import traceback
import shutil # 用于查找 libreoffice 命令和移动文件
import time   # 保留 time.sleep(0.5) 以防文件系统延迟
import logging # 导入日志模块

# --- 日志配置 ---
LOG_FILENAME = 'generation_errors.log'
logging.basicConfig(
    level=logging.WARNING, # 只记录警告及以上级别的信息
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=LOG_FILENAME,
    filemode='a' # 追加模式，每次运行不清空日志
)
# 创建一个logger实例
logger = logging.getLogger(__name__)

# --- 全局配置 ---
DEFAULT_OUTPUT_FOLDER = "output_pdfs"
DEFAULT_LIBREOFFICE_TIMEOUT = 20

# --- 通知类型配置 ---
ACCEPTANCE_TEMPLATE_PATH = "./data/录用通知模板.docx"
ACCEPTANCE_PREFIX = "录用通知"
PAGE_CHARGE_TEMPLATE_PATH = "./data/版面费模板.docx"
PAGE_CHARGE_PREFIX = "版面费通知"

# --- 辅助函数：清理 Word 内容中的标题 ---
def sanitize_title_content(title):
    """严格清理标题内容：只保留英文、数字、中文字符，其余替换为 '-'。"""
    if not isinstance(title, str):
        title = str(title)
    pattern_to_replace = r'[^a-zA-Z0-9\u4e00-\u9fff]'
    sanitized = re.sub(pattern_to_replace, '-', title)
    sanitized = re.sub(r'-+', '-', sanitized)
    sanitized = sanitized.strip('-')
    # 如果清理后为空，返回一个默认值，避免空标题
    return sanitized if sanitized else "无有效标题"

# --- 辅助函数：清理文件名中操作系统不允许的字符 ---
def sanitize_filename(filename):
    """清理文件名，移除或替换操作系统不允许的字符为 '_'。"""
    if not isinstance(filename, str):
        filename = str(filename)
    invalid_os_chars = r'[\\/*?:"<>|]'
    sanitized = re.sub(invalid_os_chars, "_", filename)
    sanitized = sanitized.strip('_')
    sanitized = re.sub(r'_+', '_', sanitized)
    # 如果清理后为空，返回一个默认值
    return sanitized if sanitized else "未命名"

# --- 辅助函数：使用 LibreOffice 转换 DOCX 为 PDF ---
def convert_docx_to_pdf_libreoffice(input_docx_path, output_pdf_path, timeout=DEFAULT_LIBREOFFICE_TIMEOUT):
    """使用 LibreOffice 命令行将 DOCX 转换为 PDF。 返回 (bool, str)"""
    output_dir = os.path.dirname(output_pdf_path)
    input_filename_base = os.path.splitext(os.path.basename(input_docx_path))[0]
    libreoffice_default_output_pdf = os.path.join(output_dir, f"{input_filename_base}.pdf")

    soffice_path = shutil.which("libreoffice") or shutil.which("soffice")
    if not soffice_path:
        error_msg = f"错误: 未找到 LibreOffice 命令。无法转换 {input_docx_path}"
        logger.error(error_msg)
        return False, error_msg

    args = [
        soffice_path, '--headless', '--norestore',
        '--convert-to', 'pdf', '--outdir', output_dir, input_docx_path
    ]
    # 不再打印执行命令 logger.info(f"Executing: {' '.join(args)}") # 可选的信息日志

    try:
        process = subprocess.run(
            args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            timeout=timeout, check=False
        )
        stdout_str = process.stdout.decode(errors='ignore')
        stderr_str = process.stderr.decode(errors='ignore')
        output_log = f"LibreOffice stdout:\n{stdout_str}\nLibreOffice stderr:\n{stderr_str}"

        if process.returncode != 0:
            err_msg = f"LibreOffice 转换失败 (返回码 {process.returncode}) for {input_docx_path}"
            logger.error(f"{err_msg}\n{output_log}") # 记录错误和日志
            if os.path.exists(libreoffice_default_output_pdf):
                try: os.remove(libreoffice_default_output_pdf)
                except OSError: pass
            return False, f"{err_msg}" # 只返回简短错误

        time.sleep(0.5) # 短暂等待文件系统

        if os.path.exists(libreoffice_default_output_pdf):
            try:
                file_size = os.path.getsize(libreoffice_default_output_pdf)
                # 不再打印文件大小 logger.info(f"Generated PDF size for {output_pdf_path}: {file_size} bytes")
                if file_size == 0:
                    err_msg = f"错误: 生成的 PDF 文件大小为 0: {output_pdf_path}"
                    logger.error(err_msg)
                    try: os.remove(libreoffice_default_output_pdf)
                    except OSError: pass
                    return False, err_msg
            except OSError as e:
                err_msg = f"错误: 无法获取生成的 PDF 文件大小 {output_pdf_path}: {e}"
                logger.error(err_msg)
                return False, err_msg

            if libreoffice_default_output_pdf != output_pdf_path:
                # 不再打印重命名 logger.info(f"Renaming {libreoffice_default_output_pdf} to {output_pdf_path}")
                try:
                    shutil.move(libreoffice_default_output_pdf, output_pdf_path)
                    # 不再打印成功 logger.info(f"Conversion successful (renamed) for {output_pdf_path}")
                    return True, "转换成功 (经重命名)"
                except Exception as e:
                    err_msg = f"重命名文件时出错 {libreoffice_default_output_pdf} -> {output_pdf_path}: {e}"
                    logger.error(err_msg, exc_info=True) # 记录异常信息
                    if os.path.exists(libreoffice_default_output_pdf):
                         try: os.remove(libreoffice_default_output_pdf)
                         except OSError: pass
                    return False, err_msg
            else:
                # 不再打印成功 logger.info(f"Conversion successful for {output_pdf_path}")
                return True, "转换成功"
        else:
            err_msg = f"命令执行完毕，但未找到输出文件: {libreoffice_default_output_pdf}"
            logger.error(f"{err_msg}\n{output_log}") # 记录错误和日志
            return False, err_msg

    except FileNotFoundError:
        err_msg = f"错误: 无法执行 LibreOffice 命令 '{soffice_path}'。"
        logger.error(err_msg)
        return False, err_msg
    except subprocess.TimeoutExpired:
        err_msg = f"错误: LibreOffice 转换超时 (超过 {timeout} 秒) for {input_docx_path}"
        logger.error(err_msg)
        return False, err_msg
    except Exception as e:
        err_msg = f"执行 LibreOffice 命令时发生未知错误 for {input_docx_path}: {e}"
        logger.error(err_msg, exc_info=True) # 记录完整异常堆栈
        return False, err_msg

# --- 主函数：生成通知 PDF (无打印，带日志记录) ---
def generate_notice_pdfs(data_list, template_path, output_prefix,
                         output_folder=DEFAULT_OUTPUT_FOLDER,
                         libreoffice_timeout=DEFAULT_LIBREOFFICE_TIMEOUT,
                         delete_docx_after_success=True):
    """根据指定模板和数据批量生成通知 PDF 文件，错误记录到日志。"""
    # 不再打印开始信息
    # logger.info(f"Starting batch generation '{output_prefix}' using template: {template_path}")

    if not os.path.exists(output_folder):
        try:
            os.makedirs(output_folder)
            # logger.info(f"Created output folder: {output_folder}")
        except OSError as e:
            logger.error(f"无法创建输出文件夹 '{output_folder}': {e}")
            return # 无法继续

    success_count = 0
    fail_count = 0
    conversion_failures = 0

    for i, data in enumerate(data_list):
        current_data = data.copy()
        original_title = current_data.get('paper_title', '无标题')
        item_identifier = f"Item {i+1} (ID: {current_data.get('paper_id', 'N/A')}, Title: '{original_title}')" # 用于日志记录
        output_docx_path = ""
        pdf_conversion_success = False # 默认转换未成功

        try:
            # --- 清理标题内容 ---
            if 'paper_title' in current_data:
                sanitized_title_for_content = sanitize_title_content(original_title)
                # logger.info(f"Sanitized title for content ({item_identifier}): {sanitized_title_for_content}")
                current_data['paper_title'] = sanitized_title_for_content
            else:
                logger.warning(f"数据中缺少 'paper_title' 字段 for {item_identifier}")
                sanitized_title_for_content = f"无标题-{current_data.get('paper_id', '未知ID')}"
            # --------------------------

            doc = DocxTemplate(template_path)
            context = current_data
            doc.render(context)

            safe_filename_part = sanitize_filename(sanitized_title_for_content)
            if not safe_filename_part or safe_filename_part == '-': # 避免文件名只有'-'
                safe_filename_part = f"无标题-{current_data.get('paper_id', '未知ID')}"
            # logger.info(f"Filename part for {item_identifier}: {safe_filename_part}")

            base_filename = f"{output_prefix}_{safe_filename_part}"
            output_docx_path = os.path.join(output_folder, f"{base_filename}.docx")
            output_pdf_path = os.path.join(output_folder, f"{base_filename}.pdf")

            # --- 保存 DOCX ---
            # logger.info(f"Saving DOCX for {item_identifier} to: {output_docx_path}")
            doc.save(output_docx_path)

            # --- 转换为 PDF ---
            # logger.info(f"Converting to PDF for {item_identifier}: {output_pdf_path}")
            conversion_ok, log_msg = convert_docx_to_pdf_libreoffice(
                output_docx_path, output_pdf_path, timeout=libreoffice_timeout
            )

            if conversion_ok:
                pdf_conversion_success = True
                success_count += 1
            else:
                # logger.error(f"PDF conversion failed for {item_identifier}. Details logged.")
                conversion_failures += 1
                # fail_count 已经在下面的 except 块或这里累加
                # 在这里不需要单独累加 fail_count，因为如果转换失败，最终会到大 except 块或在这里直接结束这次循环的成功路径

        except Exception as e:
            # 捕获这个条目处理过程中的任何错误 (模板加载、渲染、保存、转换)
            logger.error(f"处理 {item_identifier} 时出错: {e}", exc_info=True) # 记录完整异常堆栈
            fail_count += 1
            # 不需要在这里增加 conversion_failures，因为它可能在转换步骤之前失败

        finally:
            # --- 清理逻辑 ---
            # 无论 try 块是否成功，都尝试进行清理决策
            if output_docx_path and os.path.exists(output_docx_path):
                if pdf_conversion_success and delete_docx_after_success:
                    try:
                        os.remove(output_docx_path)
                        # logger.info(f"Deleted intermediate DOCX for {item_identifier}")
                    except OSError as e:
                         logger.warning(f"无法删除中间 DOCX 文件 {output_docx_path}: {e}")
                elif not pdf_conversion_success:
                     # logger.warning(f"PDF conversion failed, retaining DOCX: {output_docx_path}")
                     pass # 保留文件，不记录日志干扰
                else: # PDF 成功，但不删除 DOCX
                     # logger.info(f"PDF conversion successful, retaining DOCX as configured: {output_docx_path}")
                     pass # 保留文件

    # --- 循环结束后记录总结 ---
    logger.warning(f"'{output_prefix}' 批量任务完成。成功: {success_count}, 失败: {fail_count} (其中PDF转换失败: {conversion_failures})。日志文件: {LOG_FILENAME}")
    # 不再打印完成信息
    
    
    
    
# if __name__ == "__main__":
#     task_type = 'A'
#     # 设置任务类型: 'L', 'B', 或 'A'

#     all_notice_data = [
#         {
#             'author_names': '刘雨言,武友新,于程远',
#             'paper_title': '面向中文长文本分类场景的对抗样本攻击技术',
#             'paper_id': '2025-0016',
#             'submmit_date': '2025年2月10日',
#             'charge': '4000',
#             'time': '2025年6月10日'
#         },
#     ]

#     task_type = task_type.upper()

#     # --- 执行录用通知任务 (如果需要) ---
#     if task_type in ('L', 'A'):
#         # logger.info("Preparing to generate acceptance notices...")
#         if os.path.exists(ACCEPTANCE_TEMPLATE_PATH):
#             generate_notice_pdfs(
#                 data_list=all_notice_data,
#                 template_path=ACCEPTANCE_TEMPLATE_PATH,
#                 output_prefix=ACCEPTANCE_PREFIX
#             )
#         else:
#             logger.error(f"录用通知模板文件未找到，跳过任务: {ACCEPTANCE_TEMPLATE_PATH}")

#     # --- 执行版面费通知任务 (如果需要) ---
#     if task_type in ('B', 'A'):
#         # logger.info("Preparing to generate page charge notices...")
#         if os.path.exists(PAGE_CHARGE_TEMPLATE_PATH):
#              generate_notice_pdfs(
#                  data_list=all_notice_data,
#                  template_path=PAGE_CHARGE_TEMPLATE_PATH,
#                  output_prefix=PAGE_CHARGE_PREFIX
#              )
#         else:
#              logger.error(f"版面费通知模板文件未找到，跳过任务: {PAGE_CHARGE_TEMPLATE_PATH}")

#     if task_type not in ('L', 'B', 'A'):
#         logger.error(f"无效的任务类型: '{task_type}'. 请设置为 'L', 'B', 或 'A'.")

