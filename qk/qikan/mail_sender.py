# mail_sender.py

import smtplib
import os
import mimetypes
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional

class EmailSender:
    """
    一个用于发送邮件的类，支持单个和批量发送，以及个性化附件。
    在实例化时需要提供SMTP服务器的配置信息。
    """

    def __init__(self, smtp_server: str, smtp_port: int, sender_email: str, sender_password: str):
        """
        初始化EmailSender实例。

        :param smtp_server: SMTP服务器地址 (e.g., 'mail.cstnet.cn')
        :param smtp_port: SMTP服务器端口 (e.g., 465 for SSL)
        :param sender_email: 发件人邮箱地址
        :param sender_password: 发件人邮箱密码或授权码
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        print(f"EmailSender 已为发件人 '{self.sender_email}' 初始化。")

    def _add_attachment_to_msg(self, msg: MIMEMultipart, attachment_path: str):
        """
        辅助方法：将单个附件添加到MIMEMultipart对象。
        这是一个内部方法，不建议在类外部直接调用。
        """
        if not attachment_path or not os.path.exists(attachment_path):
            print(f"  警告: 附件路径 '{attachment_path}' 无效或文件不存在，已跳过。")
            return

        try:
            ctype, encoding = mimetypes.guess_type(attachment_path)
            if ctype is None or encoding is not None:
                ctype = 'application/octet-stream'  # 默认MIME类型
            maintype, subtype = ctype.split('/', 1)

            with open(attachment_path, 'rb') as file:
                part = MIMEBase(maintype, subtype)
                part.set_payload(file.read())
                encoders.encode_base64(part)

            filename = os.path.basename(attachment_path)
            # 使用 ('utf-8', '', filename) 格式来正确编码中文文件名
            part.add_header('Content-Disposition', 'attachment', filename=('utf-8', '', filename))
            msg.attach(part)
            print(f"  成功添加附件: {filename}")
        except Exception as e:
            print(f"  附件 '{attachment_path}' 处理失败: {e}")

    def send_single_email(self, receiver_email: str, subject: str, html_body: str, attachment_paths: Optional[List[str]] = None):
        """
        发送一封带有多个附件的邮件。

        :param receiver_email: 收件人邮箱地址
        :param subject: 邮件主题
        :param html_body: HTML格式的邮件正文
        :param attachment_paths: 附件路径的列表 (可选)
        """
        print(f"\n准备发送单封邮件至: {receiver_email}")
        
        msg = MIMEMultipart()
        msg['From'] = self.sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))

        if attachment_paths:
            print("  正在处理附件...")
            for path in attachment_paths:
                self._add_attachment_to_msg(msg, path)
        else:
            print("  无附件。")
            
        try:
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, receiver_email, msg.as_string())
            print(f"邮件成功发送至 {receiver_email}")
            return True
        except Exception as e:
            print(f"发送邮件至 {receiver_email} 失败: {e}")
            return False

    def send_bulk_personalized_emails(
        self,
        receiver_emails_list: List[str],
        unique_attachments_by_recipient: List[List[str]],
        subject: str,
        html_body: str,
        common_attachment_paths: Optional[List[str]] = None
    ):
        """
        批量发送个性化邮件，收件人邮箱和其特定附件通过索引对应。
        此方法会建立一次SMTP连接并发送所有邮件，以提高效率。

        :param receiver_emails_list: 收件人邮箱地址列表。
        :param unique_attachments_by_recipient: 嵌套列表，每个内层列表包含对应收件人的特定附件路径。
        :param subject: 邮件主题 (所有邮件统一)
        :param html_body: HTML格式的邮件正文 (所有邮件统一)
        :param common_attachment_paths: 通用附件路径列表 (可选)
        """
        if common_attachment_paths is None:
            common_attachment_paths = []

        if len(receiver_emails_list) != len(unique_attachments_by_recipient):
            print("错误：收件人邮箱列表的长度与特定附件列表的长度不匹配！操作已中止。")
            return

        print(f"\n开始批量发送任务，共计 {len(receiver_emails_list)} 封邮件...")
        try:
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.sender_email, self.sender_password)
                print("SMTP服务器已连接并登录成功，准备循环发送...")

                for i, receiver_email in enumerate(receiver_emails_list):
                    if not receiver_email:
                        print(f"\n警告: 索引 {i} 处的邮箱地址为空，已跳过。")
                        continue

                    print(f"\n--- 正在处理第 {i+1}/{len(receiver_emails_list)} 封邮件，发往: {receiver_email} ---")
                    
                    # --- 为当前收件人构建邮件 ---
                    msg = MIMEMultipart()
                    msg['From'] = self.sender_email
                    msg['To'] = receiver_email
                    msg['Subject'] = subject
                    msg.attach(MIMEText(html_body, 'html', 'utf-8'))
                    
                    # --- 准备附件列表 ---
                    unique_attachments = unique_attachments_by_recipient[i]
                    if not isinstance(unique_attachments, list):
                        print(f"  警告: 索引 {i} 处的特定附件定义不是一个列表 (而是 {type(unique_attachments)}), 已视为空附件列表处理。")
                        unique_attachments = []
                    
                    all_attachments = list(common_attachment_paths) + list(unique_attachments)
                    all_attachments = list(dict.fromkeys(all_attachments)) # 去重

                    if all_attachments:
                        print("  正在处理附件...")
                        for path in all_attachments:
                            self._add_attachment_to_msg(msg, path)
                    else:
                        print("  无附件。")
                        
                    # --- 发送邮件 ---
                    try:
                        server.sendmail(self.sender_email, receiver_email, msg.as_string())
                        print(f"  -> 邮件成功发送至 {receiver_email}")
                    except Exception as e:
                        print(f"  -> 发送邮件至 {receiver_email} 失败: {e}")

        except Exception as e:
            print(f"\n处理批量任务时发生严重错误（如登录失败）: {e}")
        
        print("\n批量发送任务执行完毕。")