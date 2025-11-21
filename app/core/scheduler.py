from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger
from app.core.config import settings

# 全局调度器单例
_scheduler: BackgroundScheduler | None = None


def get_scheduler() -> BackgroundScheduler:
    """获取或创建调度器实例"""
    global _scheduler
    if _scheduler is None:
        # 同步项目使用 BackgroundScheduler (多线程执行)
        _scheduler = BackgroundScheduler(timezone="Asia/Shanghai")
    return _scheduler


def _setup_jobs(scheduler: BackgroundScheduler):
    """
    配置定时任务清单
    """
    # scheduler.add_job(func=test, trigger=CronTrigger.from_crontab("*/1 * * * *"), id="test_job", replace_existing=True)
    pass


def start_scheduler():
    """启动调度器"""
    scheduler = get_scheduler()

    if scheduler.running:
        logger.warning("⚠️ 调度器已经在运行中，跳过启动")
        return

    # 环境检查 (避免开发环境乱跑任务)
    # 假设 .env 里配置了 ENVIRONMENT=dev
    # 你可以加一个配置项 ENABLE_SCHEDULER 来强行控制
    if settings.ENVIRONMENT == "dev":
        logger.info(f"🚧 开发环境 (DEBUG=True)，且未开启强制调度，定时任务已跳过")
        return

    try:
        _setup_jobs(scheduler)
        scheduler.start()

        # 打印任务详情
        jobs = scheduler.get_jobs()
        if jobs:
            logger.info(f"✅ 定时任务已启动，共注册 {len(jobs)} 个任务")
            for job in jobs:
                logger.info(f"   👉 Task: {job.id} | Next: {job.next_run_time}")
        else:
            logger.info("✅ 调度器已启动 (暂无挂载任务)")

    except Exception as e:
        logger.error(f"❌ 调度器启动失败: {e}")
        raise e

def stop_scheduler():
    """关闭调度器"""
    global _scheduler
    if _scheduler and _scheduler.running:
        try:
            _scheduler.shutdown(wait=True)
            logger.info("🛑 定时任务调度器已关闭")
        except Exception as e:
            logger.error(f"❌ 关闭调度器失败: {e}")
