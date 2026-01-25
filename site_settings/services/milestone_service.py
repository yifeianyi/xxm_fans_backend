from typing import List, Optional
from django.db.models import QuerySet

from site_settings.models import Milestone
from core.exceptions import ValidationException, DatabaseException


class MilestoneService:
    """里程碑服务类"""

    @staticmethod
    def get_all_milestones() -> QuerySet[Milestone]:
        """
        获取所有里程碑
        """
        try:
            return Milestone.objects.all().order_by('-date', 'display_order')
        except Exception as e:
            raise DatabaseException(f"获取里程碑列表失败: {str(e)}")

    @staticmethod
    def get_milestone_by_id(milestone_id: int) -> Optional[Milestone]:
        """
        根据ID获取里程碑
        """
        try:
            return Milestone.objects.get(id=milestone_id)
        except Milestone.DoesNotExist:
            return None
        except Exception as e:
            raise DatabaseException(f"获取里程碑失败: {str(e)}")

    @staticmethod
    def create_milestone(date: str, title: str, description: str, display_order: int = 0) -> Milestone:
        """
        创建里程碑
        """
        try:
            if not date or not title or not description:
                raise ValidationException("日期、标题和描述不能为空")

            milestone = Milestone.objects.create(
                date=date,
                title=title,
                description=description,
                display_order=display_order
            )
            return milestone
        except ValidationException:
            raise
        except Exception as e:
            raise DatabaseException(f"创建里程碑失败: {str(e)}")

    @staticmethod
    def update_milestone(milestone_id: int, date: str = None, title: str = None,
                         description: str = None, display_order: int = None) -> Milestone:
        """
        更新里程碑
        """
        try:
            milestone = MilestoneService.get_milestone_by_id(milestone_id)
            if not milestone:
                raise ValidationException("里程碑不存在")

            if date is not None:
                milestone.date = date
            if title is not None:
                milestone.title = title
            if description is not None:
                milestone.description = description
            if display_order is not None:
                milestone.display_order = display_order

            milestone.save()
            return milestone
        except ValidationException:
            raise
        except Exception as e:
            raise DatabaseException(f"更新里程碑失败: {str(e)}")

    @staticmethod
    def delete_milestone(milestone_id: int) -> bool:
        """
        删除里程碑
        """
        try:
            milestone = MilestoneService.get_milestone_by_id(milestone_id)
            if not milestone:
                raise ValidationException("里程碑不存在")

            milestone.delete()
            return True
        except ValidationException:
            raise
        except Exception as e:
            raise DatabaseException(f"删除里程碑失败: {str(e)}")