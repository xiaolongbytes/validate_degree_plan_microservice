from flask import Flask, request, jsonify

app = Flask(__name__)

def find_required_courses(all_courses):
    """From a list of all course objects, return a list of required courses"""
    required_courses = {}
    for course in all_courses:
        if course['isRequired']:
            required_courses[course['courseCode']] = course['fullName']
    
    return required_courses

def find_course_from_ID(course_ID, all_courses):
    """Find the course object given the course ID"""
    for course in all_courses:
        if course['id'] == course_ID:
            return course


@app.route('/validate_degree_plan', methods=['POST'])
def validate_degree_plan():
    failedValidations = []

    data = request.get_json()

    degree_plan = data['serverDegreePlan']
    courses = data['courses']

    required_courses = find_required_courses(courses)
    elective_courses = {}
    taken_courses = set()
    missing_prerequisites = []

    for degree_plan_quarter in degree_plan:
        for course in degree_plan_quarter['coursesAssigned']:
            # Check prerequisites
            for prerequisiteID in course['prerequisiteCourseIDs']:
                prerequisite = find_course_from_ID(prerequisiteID, courses)
                if prerequisite['courseCode'] not in taken_courses:
                    missing_prerequisites.append(f"{degree_plan_quarter['quarter']['season']} {degree_plan_quarter['quarter']['year']} {course['courseCode']} is missing prerequisites {prerequisite['courseCode']}")
            # Check Required/Electives
            if course['isRequired']:
                required_courses.pop(course['courseCode'])
            else:
                elective_courses[course['courseCode']] = course['fullName']
            # Update taken courses
            taken_courses.add(course['courseCode'])

    if len(required_courses) > 0:
        missing_courses = []
        for course_code, course_name in required_courses.items():
            missing_courses.append(f"{course_code}: {course_name}")
        missing_courses_string = ", ".join(missing_courses)
        failedValidations.append(f" Missing the following required courses: {missing_courses_string}")

    if len(elective_courses) < 3:
        failedValidations.append(" Degree requirement of 3 electives has not been met.")

    if len(missing_prerequisites) > 0:
        missing_prerequisites_string = ", ".join(missing_prerequisites)
        failedValidations.append(f" The following quarters and courses are missing their prerequisite(s): {missing_prerequisites_string}")

    if len(failedValidations) > 0:
        return jsonify({'isValid': False, 'failedValidations': failedValidations})
    return jsonify({'isValid': True, 'failedValidations': failedValidations})

if __name__ == '__main__':
    app.run(debug=True, port=5003)