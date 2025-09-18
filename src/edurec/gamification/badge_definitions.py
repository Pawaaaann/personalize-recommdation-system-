#!/usr/bin/env python3
"""
Badge definitions and achievement system.
"""

from typing import Optional
from .models import Badge, BadgeType, BadgeRarity

# Define all available badges
BADGES = {
    # Streak Badges
    "first_streak": Badge(
        id="first_streak",
        name="Getting Started",
        description="Complete your first day of learning",
        type=BadgeType.STREAK,
        rarity=BadgeRarity.COMMON,
        icon="🌱",
        requirements={"current_streak": 1},
        points=50,
        color="text-green-600 bg-green-100"
    ),
    
    "week_warrior": Badge(
        id="week_warrior",
        name="Week Warrior",
        description="Learn for 7 consecutive days",
        type=BadgeType.STREAK,
        rarity=BadgeRarity.RARE,
        icon="🔥",
        requirements={"current_streak": 7},
        points=200,
        color="text-orange-600 bg-orange-100"
    ),
    
    "month_master": Badge(
        id="month_master",
        name="Month Master",
        description="Maintain a 30-day learning streak",
        type=BadgeType.STREAK,
        rarity=BadgeRarity.EPIC,
        icon="🏆",
        requirements={"current_streak": 30},
        points=500,
        color="text-purple-600 bg-purple-100"
    ),
    
    "streak_legend": Badge(
        id="streak_legend",
        name="Streak Legend",
        description="Achieve a 100-day learning streak",
        type=BadgeType.STREAK,
        rarity=BadgeRarity.LEGENDARY,
        icon="👑",
        requirements={"current_streak": 100},
        points=1000,
        color="text-yellow-600 bg-yellow-100"
    ),
    
    # Completion Badges
    "first_course": Badge(
        id="first_course",
        name="First Steps",
        description="Complete your first course",
        type=BadgeType.COMPLETION,
        rarity=BadgeRarity.COMMON,
        icon="📚",
        requirements={"courses_completed": 1},
        points=100,
        color="text-blue-600 bg-blue-100"
    ),
    
    "course_collector": Badge(
        id="course_collector",
        name="Course Collector",
        description="Complete 10 courses",
        type=BadgeType.COMPLETION,
        rarity=BadgeRarity.RARE,
        icon="📖",
        requirements={"courses_completed": 10},
        points=300,
        color="text-indigo-600 bg-indigo-100"
    ),
    
    "knowledge_seeker": Badge(
        id="knowledge_seeker",
        name="Knowledge Seeker",
        description="Complete 25 courses",
        type=BadgeType.COMPLETION,
        rarity=BadgeRarity.EPIC,
        icon="🎓",
        requirements={"courses_completed": 25},
        points=750,
        color="text-purple-600 bg-purple-100"
    ),
    
    "master_learner": Badge(
        id="master_learner",
        name="Master Learner",
        description="Complete 50+ courses",
        type=BadgeType.COMPLETION,
        rarity=BadgeRarity.LEGENDARY,
        icon="🧠",
        requirements={"courses_completed": 50},
        points=1500,
        color="text-pink-600 bg-pink-100"
    ),
    
    # Exploration Badges
    "curious_mind": Badge(
        id="curious_mind",
        name="Curious Mind",
        description="Explore 3 different domains",
        type=BadgeType.EXPLORATION,
        rarity=BadgeRarity.COMMON,
        icon="🔍",
        requirements={"domains_explored_count": 3},
        points=150,
        color="text-teal-600 bg-teal-100"
    ),
    
    "polymath": Badge(
        id="polymath",
        name="Polymath",
        description="Explore 5+ different domains",
        type=BadgeType.EXPLORATION,
        rarity=BadgeRarity.RARE,
        icon="🌟",
        requirements={"domains_explored_count": 5},
        points=400,
        color="text-cyan-600 bg-cyan-100"
    ),
    
    # Consistency Badges
    "weekend_learner": Badge(
        id="weekend_learner",
        name="Weekend Learner",
        description="Learn on 10 different weekends",
        type=BadgeType.CONSISTENCY,
        rarity=BadgeRarity.RARE,
        icon="📅",
        requirements={"weekend_days": 10},
        points=250,
        color="text-emerald-600 bg-emerald-100"
    ),
    
    "early_bird": Badge(
        id="early_bird",
        name="Early Bird",
        description="Start learning before 8 AM on 5 different days",
        type=BadgeType.CONSISTENCY,
        rarity=BadgeRarity.EPIC,
        icon="🌅",
        requirements={"early_sessions": 5},
        points=300,
        color="text-amber-600 bg-amber-100"
    ),
    
    # Milestone Badges
    "xp_rookie": Badge(
        id="xp_rookie",
        name="XP Rookie",
        description="Earn your first 1,000 XP",
        type=BadgeType.MILESTONE,
        rarity=BadgeRarity.COMMON,
        icon="⭐",
        requirements={"total_xp": 1000},
        points=100,
        color="text-gray-600 bg-gray-100"
    ),
    
    "xp_veteran": Badge(
        id="xp_veteran",
        name="XP Veteran",
        description="Earn 5,000+ XP",
        type=BadgeType.MILESTONE,
        rarity=BadgeRarity.RARE,
        icon="💎",
        requirements={"total_xp": 5000},
        points=500,
        color="text-blue-600 bg-blue-100"
    ),
    
    "xp_champion": Badge(
        id="xp_champion",
        name="XP Champion",
        description="Earn 10,000+ XP",
        type=BadgeType.MILESTONE,
        rarity=BadgeRarity.EPIC,
        icon="🏅",
        requirements={"total_xp": 10000},
        points=1000,
        color="text-red-600 bg-red-100"
    ),
    
    # Social Badges
    "feedback_giver": Badge(
        id="feedback_giver",
        name="Feedback Giver",
        description="Rate or like 20+ courses",
        type=BadgeType.EXPLORATION,
        rarity=BadgeRarity.COMMON,
        icon="👍",
        requirements={"courses_liked": 20},
        points=150,
        color="text-green-600 bg-green-100"
    ),
    
    # Specialization Badges (Dynamic based on domains)
    "tech_specialist": Badge(
        id="tech_specialist",
        name="Tech Specialist",
        description="Complete 10+ courses in Technology",
        type=BadgeType.SPECIALIZATION,
        rarity=BadgeRarity.RARE,
        icon="💻",
        requirements={"domain_courses": {"technology": 10}},
        points=400,
        color="text-slate-600 bg-slate-100"
    ),
    
    "business_guru": Badge(
        id="business_guru",
        name="Business Guru",
        description="Complete 10+ courses in Business",
        type=BadgeType.SPECIALIZATION,
        rarity=BadgeRarity.RARE,
        icon="💼",
        requirements={"domain_courses": {"business": 10}},
        points=400,
        color="text-stone-600 bg-stone-100"
    ),
    
    "creative_soul": Badge(
        id="creative_soul",
        name="Creative Soul",
        description="Complete 10+ courses in Arts & Design",
        type=BadgeType.SPECIALIZATION,
        rarity=BadgeRarity.RARE,
        icon="🎨",
        requirements={"domain_courses": {"arts": 10}},
        points=400,
        color="text-rose-600 bg-rose-100"
    )
}

def get_badge(badge_id: str) -> Optional[Badge]:
    """Get badge by ID."""
    return BADGES.get(badge_id)

def get_all_badges() -> dict:
    """Get all available badges."""
    return BADGES

def get_badges_by_type(badge_type: BadgeType) -> dict:
    """Get badges of a specific type."""
    return {k: v for k, v in BADGES.items() if v.type == badge_type}

def get_badges_by_rarity(rarity: BadgeRarity) -> dict:
    """Get badges of a specific rarity."""
    return {k: v for k, v in BADGES.items() if v.rarity == rarity}