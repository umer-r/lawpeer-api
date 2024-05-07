from api.database import db
from api.models.user import Lawyer
from api.models.skill import Skill
from api.utils.status_codes import Status

def get_all_skills():
    return Skill.query.all()

def get_lawyer_skills(id):
    lawyer = Lawyer.query.get(id)
    if lawyer:
        lawyer_skills = [{"id": skill.id, "name": skill.name} for skill in lawyer.skills]
        if lawyer_skills:
            return lawyer_skills
    return None

def filter_lawyer_by_skill(id):
    skill = Skill.query.get(id)
    if skill:
        lawyers = skill.lawyers.all()
        if lawyers:
            return lawyers
        else: 
            return None, True
    else:
        return None, False

def add_skills_to_lawyer(lawyer_id, skill_ids):
    lawyer = Lawyer.query.get(lawyer_id)
    if not lawyer:
        return {'error': 'Lawyer not found'}, Status.HTTP_404_NOT_FOUND
    
    if not skill_ids:  # Check if skill_ids is empty
        # Remove all skills from the lawyer's profile
        lawyer.skills = []
        db.session.commit()
        return {'message': 'All skills removed from lawyer profile'}, Status.HTTP_200_OK
    
    # Check if the lawyer already has 5 skills
    if len(skill_ids) >= 6:
        return {'error': 'Can not add more than 5 skills'}, Status.HTTP_400_BAD_REQUEST
    
    # Remove previously added skills
    lawyer.skills = []
    
    for skill_id in skill_ids:
        skill = Skill.query.get(skill_id)
        if not skill:
            return {'error': f'Skill with ID {skill_id} not found'}, Status.HTTP_404_NOT_FOUND
        
        if skill not in lawyer.skills:
            lawyer.skills.append(skill)
    
    db.session.commit()

    return {'message': f'Skills added to lawyer {lawyer_id}'}, Status.HTTP_200_OK

def get_skills_of_all_lawyers():
    lawyers_skills = {}
    lawyers = Lawyer.query.all()

    if lawyers:
        for lawyer in lawyers:
            lawyer_skills = [skill.name for skill in lawyer.skills]
            lawyers_skills[lawyer.id] = lawyer_skills
    else:
        return None, False
    
    if lawyers_skills:
        return lawyers_skills
    else:
        return None, False