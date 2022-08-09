"""
Tests for CaeTools API views.
"""

# System Imports.
from django.core.management.color import color_style
from django_expanded_test_cases import IntegrationTestCase

# User Imports.
from cae_home import models
from cae_home.management.commands.seeders import user as user_seeds
from cae_home.management.commands.seeders import wmu as wmu_seeds


class ApiViewTests(IntegrationTestCase):
    """
    Tests for various API views.
    """
    # Currently not needed. So url was commented out for security.
    # def test__get_wmu_user(self):
    #     """Tests API view for getting WmuUser models."""
    #     # Generate model seeds.
    #     wmu_seeds.create_departments(color_style())
    #     wmu_seeds.create_majors(color_style())
    #     user_seeds.create_addresses(color_style(), 10)
    #     user_seeds.create_wmu_users(color_style(), 10)
    #
    #     with self.subTest('With empty value'):
    #         self.assertGetResponse(
    #             'cae_tools:api_wmu_user',
    #             expected_content="""
    #                 {
    #                     "bronco_net": null,
    #                     "winno": null,
    #                     "first_name": null,
    #                     "middle_name": null,
    #                     "last_name": null,
    #                     "user_type": null,
    #                     "is_active": null,
    #                     "official_email": null
    #                 }
    #             """
    #         )
    #
    #     with self.subTest('With bad value'):
    #         self.assertGetResponse(
    #             'cae_tools:api_wmu_user',
    #             data={'identifier': 'BadValue'},
    #             expected_content="""
    #                 {
    #                     "bronco_net": null,
    #                     "winno": null,
    #                     "first_name": null,
    #                     "middle_name": null,
    #                     "last_name": null,
    #                     "user_type": null,
    #                     "is_active": null,
    #                     "official_email": null
    #                 }
    #             """
    #         )
    #
    #     with self.subTest('With partial values'):
    #         wmu_user = models.WmuUser.objects.first()
    #         self.assertGetResponse(
    #             'cae_tools:api_wmu_user',
    #             data={'identifier': '{0}'.format(str(wmu_user.bronco_net)[3:])},
    #             expected_content="""
    #                 {
    #                     "bronco_net": null,
    #                     "winno": null,
    #                     "first_name": null,
    #                     "middle_name": null,
    #                     "last_name": null,
    #                     "user_type": null,
    #                     "is_active": null,
    #                     "official_email": null
    #                 }
    #             """
    #         )
    #         self.assertGetResponse(
    #             'cae_tools:api_wmu_user',
    #             data={'identifier': '{0}'.format(str(wmu_user.winno)[:3])},
    #             expected_content="""
    #                 {
    #                     "bronco_net": null,
    #                     "winno": null,
    #                     "first_name": null,
    #                     "middle_name": null,
    #                     "last_name": null,
    #                     "user_type": null,
    #                     "is_active": null,
    #                     "official_email": null
    #                 }
    #             """
    #         )
    #
    #     # Get list of all WmuUser models.
    #     wmu_user_list = models.WmuUser.objects.all()
    #
    #     # For each model, make an API call and verify expected values come back.
    #     for index in range(len(wmu_user_list)):
    #         # Only test first 10 models in list. If those pass, then all probably will.
    #         if index > 10:
    #             continue
    #
    #         wmu_user = wmu_user_list[index]
    #
    #         # Check each individual WmuUser as a subtest.
    #         with self.subTest('With "{0}" wmu_user'.format(wmu_user)):
    #
    #             # Determine expected values from each field of current model.
    #             bronco_net = wmu_user.bronco_net
    #             bronco_net = '"{0}"'.format(bronco_net) if bronco_net else 'null'
    #             winno = wmu_user.winno
    #             winno = '"{0}"'.format(winno) if winno else 'null'
    #             first_name = wmu_user.first_name
    #             first_name = '"{0}"'.format(first_name) if first_name else 'null'
    #             middle_name = wmu_user.middle_name
    #             middle_name = '"{0}"'.format(middle_name) if middle_name else 'null'
    #             last_name = wmu_user.last_name
    #             last_name = '"{0}"'.format(last_name) if last_name else 'null'
    #             is_active = wmu_user.is_active
    #             is_active = 'true' if is_active else 'false'
    #
    #             # Check querying by bronco_net.
    #             self.assertGetResponse(
    #                 'cae_tools:api_wmu_user',
    #                 data={'identifier': str(wmu_user.bronco_net).upper()},
    #                 expected_content=[
    #                     '"bronco_net": {0},'.format(bronco_net),
    #                     '"winno": {0},'.format(winno),
    #                     '"first_name": {0},'.format(first_name),
    #                     '"middle_name": {0},'.format(middle_name),
    #                     '"last_name": {0},'.format(last_name),
    #                     '"user_type": {0},'.format(wmu_user.user_type),
    #                     '"is_active": {0},'.format(is_active),
    #                     '"official_email": "{0}"'.format(wmu_user.official_email),
    #                 ]
    #             )
    #             self.assertGetResponse(
    #                 'cae_tools:api_wmu_user',
    #                 data={'identifier': str(wmu_user.bronco_net).lower()},
    #                 expected_content=[
    #                     '"bronco_net": {0},'.format(bronco_net),
    #                     '"winno": {0},'.format(winno),
    #                     '"first_name": {0},'.format(first_name),
    #                     '"middle_name": {0},'.format(middle_name),
    #                     '"last_name": {0},'.format(last_name),
    #                     '"user_type": {0},'.format(wmu_user.user_type),
    #                     '"is_active": {0},'.format(is_active),
    #                     '"official_email": "{0}"'.format(wmu_user.official_email),
    #                 ]
    #             )
    #             # Check querying by winno.
    #             self.assertGetResponse(
    #                 'cae_tools:api_wmu_user',
    #                 data={'identifier': str(wmu_user.winno).upper()},
    #                 expected_content=[
    #                     '"bronco_net": {0},'.format(bronco_net),
    #                     '"winno": {0},'.format(winno),
    #                     '"first_name": {0},'.format(first_name),
    #                     '"middle_name": {0},'.format(middle_name),
    #                     '"last_name": {0},'.format(last_name),
    #                     '"user_type": {0},'.format(wmu_user.user_type),
    #                     '"is_active": {0},'.format(is_active),
    #                     '"official_email": "{0}"'.format(wmu_user.official_email),
    #                 ]
    #             )
    #             self.assertGetResponse(
    #                 'cae_tools:api_wmu_user',
    #                 data={'identifier': str(wmu_user.winno).lower()},
    #                 expected_content=[
    #                     '"bronco_net": {0},'.format(bronco_net),
    #                     '"winno": {0},'.format(winno),
    #                     '"first_name": {0},'.format(first_name),
    #                     '"middle_name": {0},'.format(middle_name),
    #                     '"last_name": {0},'.format(last_name),
    #                     '"user_type": {0},'.format(wmu_user.user_type),
    #                     '"is_active": {0},'.format(is_active),
    #                     '"official_email": "{0}"'.format(wmu_user.official_email),
    #                 ]
    #             )

    def test__get_department(self):
        """Tests API view for getting Department models."""
        # Generate model seeds.
        wmu_seeds.create_departments(color_style())

        with self.subTest('With empty value'):
            self.assertGetResponse(
                'cae_tools:api_department',
                expected_content='{"name": null}'
            )

        with self.subTest('With bad value'):
            self.assertGetResponse(
                'cae_tools:api_department',
                data={'identifier': 'BadValue'},
                expected_content='{"name": null}'
            )

        with self.subTest('With partial values'):
            self.assertGetResponse(
                'cae_tools:api_department',
                data={'identifier': 'Computer'},
                expected_content='{"name": null}'
            )
            self.assertGetResponse(
                'cae_tools:api_department',
                data={'identifier': 'Science'},
                expected_content='{"name": null}'
            )

        # Get list of all Department models.
        department_list = models.Department.objects.all()

        # For each model, make an API call and verify expected values come back.
        for index in range(len(department_list)):
            # Only test first 10 models in list. If those pass, then all probably will.
            if index > 10:
                continue

            department = department_list[index]

            # Check each individual Department as a subtest.
            with self.subTest('With "{0}" department'.format(department)):

                # Check querying by name.
                self.assertGetResponse(
                    'cae_tools:api_department',
                    data={'identifier': str(department.name).upper()},
                    expected_content='{"name": "' + str(department.name) + '"}'
                )
                self.assertGetResponse(
                    'cae_tools:api_department',
                    data={'identifier': str(department.name).lower()},
                    expected_content='{"name": "' + str(department.name) + '"}'
                )
                # Check querying by slug.
                self.assertGetResponse(
                    'cae_tools:api_department',
                    data={'identifier': department.slug},
                    expected_content='{"name": "' + str(department.name) + '"}'
                )

    def test__get_room_type(self):
        """Tests API view for getting RoomType models."""
        # Generate model seeds.
        wmu_seeds.create_room_types(color_style())

        with self.subTest('With empty value'):
            self.assertGetResponse(
                'cae_tools:api_room_type',
                expected_content='{"name": null}'
            )

        with self.subTest('With bad value'):
            self.assertGetResponse(
                'cae_tools:api_room_type',
                data={'identifier': 'BadValue'},
                expected_content='{"name": null}'
            )

        with self.subTest('With partial values'):
            self.assertGetResponse(
                'cae_tools:api_room_type',
                data={'identifier': 'Computer'},
                expected_content='{"name": null}'
            )
            self.assertGetResponse(
                'cae_tools:api_room_type',
                data={'identifier': 'Lab'},
                expected_content='{"name": null}'
            )

        # Get list of all RoomType models.
        room_type_list = models.RoomType.objects.all()

        # For each model, make an API call and verify expected values come back.
        for index in range(len(room_type_list)):
            # Only test first 10 models in list. If those pass, then all probably will.
            if index > 10:
                continue

            room_type = room_type_list[index]

            # Check each individual RoomType as a subtest.
            with self.subTest('With "{0}" room_type'.format(room_type)):
                # Check querying by name.
                self.assertGetResponse(
                    'cae_tools:api_room_type',
                    data={'identifier': str(room_type.name).upper()},
                    expected_content='{"name": "' + str(room_type.name) + '"}'
                )
                self.assertGetResponse(
                    'cae_tools:api_room_type',
                    data={'identifier': str(room_type.name).lower()},
                    expected_content='{"name": "' + str(room_type.name) + '"}'
                )
                # Check querying by slug.
                self.assertGetResponse(
                    'cae_tools:api_room_type',
                    data={'identifier': room_type.slug},
                    expected_content='{"name": "' + str(room_type.name) + '"}'
                )

    def test__get_room(self):
        """Tests API view for getting Room models."""
        # Generate model seeds.
        wmu_seeds.create_departments(color_style())
        wmu_seeds.create_room_types(color_style())
        wmu_seeds.create_rooms(color_style())

        with self.subTest('With empty value'):
            self.assertGetResponse(
                'cae_tools:api_room',
                expected_content=[
                    '"department": null,',
                    '"room_type": null,',
                    '"name": null,',
                    '"description": null,',
                    '"capacity": null',
                ],
            )

        with self.subTest('With bad value'):
            self.assertGetResponse(
                'cae_tools:api_room',
                data={'identifier': 'BadValue'},
                expected_content=[
                    '"department": null,',
                    '"room_type": null,',
                    '"name": null,',
                    '"description": null,',
                    '"capacity": null',
                ],
            )

        with self.subTest('With partial values'):
            self.assertGetResponse(
                'cae_tools:api_room',
                data={'identifier': 'C-'},
                expected_content=[
                    '"department": null,',
                    '"room_type": null,',
                    '"name": null,',
                    '"description": null,',
                    '"capacity": null',
                ],
            )
            self.assertGetResponse(
                'cae_tools:api_room',
                data={'identifier': '220'},
                expected_content=[
                    '"department": null,',
                    '"room_type": null,',
                    '"name": null,',
                    '"description": null,',
                    '"capacity": null',
                ],
            )

        # Get list of all Room models.
        room_list = models.Room.objects.all()

        # For each model, make an API call and verify expected values come back.
        for index in range(len(room_list)):
            # Only test first 10 models in list. If those pass, then all probably will.
            if index > 10:
                continue

            room = room_list[index]

            # Determine expected values from each field of current model.
            department = room.department.all()
            department = '","'.join(str(x.pk) for x in department) if department else 'null'
            room_type = room.room_type
            room_type = str(room_type.pk) if room_type else 'null'

            # Check each individual Room as a subtest.
            with self.subTest('With "{0}" room'.format(room)):
                # Check querying by name.
                self.assertGetResponse(
                    'cae_tools:api_room',
                    data={'identifier': str(room.name).upper()},
                    expected_content=[
                        '"department": ' + department + ',',
                        '"room_type": ' + room_type + ',',
                        '"name": "' + str(room.name) + '",',
                        '"description": "' + str(room.description) + '",',
                        '"capacity": ' + str(room.capacity) + '',
                    ],
                )
                self.assertGetResponse(
                    'cae_tools:api_room',
                    data={'identifier': str(room.name).lower()},
                    expected_content=[
                        '"department": ' + department + ',',
                        '"room_type": ' + room_type + ',',
                        '"name": "' + str(room.name) + '",',
                        '"description": "' + str(room.description) + '",',
                        '"capacity": ' + str(room.capacity) + '',
                    ],
                )
                # Check querying by slug.
                self.assertGetResponse(
                    'cae_tools:api_room',
                    data={'identifier': room.slug},
                    expected_content=[
                        '"department": ' + department + ',',
                        '"room_type": ' + room_type + ',',
                        '"name": "' + str(room.name) + '",',
                        '"description": "' + str(room.description) + '",',
                        '"capacity": ' + str(room.capacity) + '',
                    ],
                )

    def test__get_major(self):
        """Tests API view for getting Major models."""
        # Generate model seeds.
        wmu_seeds.create_departments(color_style())
        wmu_seeds.create_majors(color_style())

        with self.subTest('With empty value'):
            self.assertGetResponse(
                'cae_tools:api_major',
                expected_content=[
                    '"department": null,',
                    '"student_code": null,',
                    '"program_code": null,',
                    '"name": null,',
                    '"degree_level": null,',
                    '"is_active": null',
                ],
            )

        with self.subTest('With bad value'):
            self.assertGetResponse(
                'cae_tools:api_major',
                data={'identifier': 'BadValue'},
                expected_content=[
                    '"department": null,',
                    '"student_code": null,',
                    '"program_code": null,',
                    '"name": null,',
                    '"degree_level": null,',
                    '"is_active": null',
                ],
            )

        with self.subTest('With partial values'):
            self.assertGetResponse(
                'cae_tools:api_major',
                data={'identifier': 'CS'},
                expected_content=[
                    '"department": null,',
                    '"student_code": null,',
                    '"program_code": null,',
                    '"name": null,',
                    '"degree_level": null,',
                    '"is_active": null',
                ],
            )
            self.assertGetResponse(
                'cae_tools:api_major',
                data={'identifier': 'IJ'},
                expected_content=[
                    '"department": null,',
                    '"student_code": null,',
                    '"program_code": null,',
                    '"name": null,',
                    '"degree_level": null,',
                    '"is_active": null',
                ],
            )

        # Get list of all Major models.
        major_list = models.Major.objects.all()

        # For each model, make an API call and verify expected values come back.
        for index in range(len(major_list)):
            # Only test first 10 models in list. If those pass, then all probably will.
            if index > 10:
                continue

            major = major_list[index]

            # Determine expected values from each field of current model.
            department = major.department
            department = str(department.pk) if department else 'null'
            is_active = major.is_active
            is_active = 'true' if is_active else 'false'

            # Check each individual Major as a subtest.
            with self.subTest('With "{0}" major'.format(major)):
                # Check querying by StudentCode.
                self.assertGetResponse(
                    'cae_tools:api_major',
                    data={'identifier': str(major.student_code).upper()},
                    expected_content=[
                        '"department": ' + department + ',',
                        '"student_code": "' + str(major.student_code) + '",',
                        '"program_code": "' + str(major.program_code) + '",',
                        '"name": "' + str(major.name) + '",',
                        '"degree_level": ' + str(major.degree_level) + ',',
                        '"is_active": ' + is_active + '',
                    ],
                )
                self.assertGetResponse(
                    'cae_tools:api_major',
                    data={'identifier': str(major.student_code).lower()},
                    expected_content=[
                        '"department": ' + department + ',',
                        '"student_code": "' + str(major.student_code) + '",',
                        '"program_code": "' + str(major.program_code) + '",',
                        '"name": "' + str(major.name) + '",',
                        '"degree_level": ' + str(major.degree_level) + ',',
                        '"is_active": ' + is_active + '',
                    ],
                )
                # Check querying by ProgramCode.
                self.assertGetResponse(
                    'cae_tools:api_major',
                    data={'identifier': str(major.program_code).upper()},
                    expected_content=[
                        '"department": ' + department + ',',
                        '"student_code": "' + str(major.student_code) + '",',
                        '"program_code": "' + str(major.program_code) + '",',
                        '"name": "' + str(major.name) + '",',
                        '"degree_level": ' + str(major.degree_level) + ',',
                        '"is_active": ' + is_active + '',
                    ],
                )
                self.assertGetResponse(
                    'cae_tools:api_major',
                    data={'identifier': str(major.program_code).lower()},
                    expected_content=[
                        '"department": ' + department + ',',
                        '"student_code": "' + str(major.student_code) + '",',
                        '"program_code": "' + str(major.program_code) + '",',
                        '"name": "' + str(major.name) + '",',
                        '"degree_level": ' + str(major.degree_level) + ',',
                        '"is_active": ' + is_active + '',
                    ],
                )
                # Check querying by slug.
                self.assertGetResponse(
                    'cae_tools:api_major',
                    data={'identifier': major.slug},
                    expected_content=[
                        '"department": ' + department + ',',
                        '"student_code": "' + str(major.student_code) + '",',
                        '"program_code": "' + str(major.program_code) + '",',
                        '"name": "' + str(major.name) + '",',
                        '"degree_level": ' + str(major.degree_level) + ',',
                        '"is_active": ' + is_active + '',
                    ],
                )

    # TODO: Cannot test this without seeds first.
    # def test__get_class(self):
    #     """Tests API view for getting Class models."""
    #     # Generate model seeds.
    #     wmu_seeds.create_wmu_classes(color_style())
    #
    #     with self.subTest('With empty value'):
    #         self.assertGetResponse(
    #             'cae_tools:api_wmu_class',
    #             expected_content='{"name": null}'
    #         )
    #
    #     with self.subTest('With bad value'):
    #         self.assertGetResponse(
    #             'cae_tools:api_wmu_class',
    #             data={'identifier': 'BadValue'},
    #             expected_content='{"name": null}'
    #         )
    #
    #     with self.subTest('With partial values'):
    #         self.assertGetResponse(
    #             'cae_tools:api_wmu_class',
    #             data={'identifier': 'Computer'},
    #             expected_content='{"name": null}'
    #         )
    #         self.assertGetResponse(
    #             'cae_tools:api_wmu_class',
    #             data={'identifier': 'Science'},
    #             expected_content='{"name": null}'
    #         )
    #
    #     # Get list of all WmuClass models.
    #     wmu_class_list = models.WmuClass.objects.all()
    #
    #     # For each model, make an API call and verify expected values come back.
    #     for wmu_class in wmu_class_list:
    #         # Check each individual WmuClass as a subtest.
    #         with self.subTest('With "{0}" wmu_class'.format(wmu_class)):
    #             # Check querying by name.
    #             self.assertGetResponse(
    #                 'cae_tools:api_wmu_class',
    #                 data={'identifier': str(wmu_class.name).upper()},
    #                 expected_content='{"name": "' + str(wmu_class.name) + '"}'
    #             )
    #             self.assertGetResponse(
    #                 'cae_tools:api_wmu_class',
    #                 data={'identifier': str(wmu_class.name).lower()},
    #                 expected_content='{"name": "' + str(wmu_class.name) + '"}'
    #             )
    #             # Check querying by slug.
    #             self.assertGetResponse(
    #                 'cae_tools:api_wmu_class',
    #                 data={'identifier': wmu_class.slug},
    #                 expected_content='{"name": "' + wmu_class.name + '"}'
    #             )

    def test__get_semester(self):
        """Tests API view for getting Semester models."""
        # Generate model seeds.
        wmu_seeds.create_semesters(color_style())

        semester = models.Semester.objects.first()
        self.assertGetResponse(
            'cae_tools:api_semester',
            data={'identifier': str(semester.name).upper()},
            expected_content=[
                '"name": "' + str(semester.name) + '",',
                '"start_date": "' + str(semester.start_date) + '",',
                '"end_date": "' + str(semester.end_date) + '"',
            ],
        )

        with self.subTest('With empty value'):
            self.assertGetResponse(
                'cae_tools:api_semester',
                expected_content=[
                    '"name": null,',
                    '"start_date": null,',
                    '"end_date": null',
                ],
            )

        with self.subTest('With bad value'):
            self.assertGetResponse(
                'cae_tools:api_semester',
                data={'identifier': 'BadValue'},
                expected_content=[
                    '"name": null,',
                    '"start_date": null,',
                    '"end_date": null',
                ],
            )

        with self.subTest('With partial values'):
            self.assertGetResponse(
                'cae_tools:api_semester',
                data={'identifier': 'Fall'},
                expected_content=[
                    '"name": null,',
                    '"start_date": null,',
                    '"end_date": null',
                ],
            )
            self.assertGetResponse(
                'cae_tools:api_semester',
                data={'identifier': '2020'},
                expected_content=[
                    '"name": null,',
                    '"start_date": null,',
                    '"end_date": null',
                ],
            )

        # Get list of all Semester models.
        semester_list = models.Semester.objects.all()

        # For each model, make an API call and verify expected values come back.
        for index in range(len(semester_list)):
            # Only test first 10 models in list. If those pass, then all probably will.
            if index > 10:
                continue

            semester = semester_list[index]

            # Check each individual Semester as a subtest.
            with self.subTest('With "{0}" semester'.format(semester)):
                # Check querying by name.
                self.assertGetResponse(
                    'cae_tools:api_semester',
                    data={'identifier': str(semester.name).upper()},
                    expected_content=[
                        '"name": "' + str(semester.name) + '",',
                        '"start_date": "' + str(semester.start_date) + '",',
                        '"end_date": "' + str(semester.end_date) + '"',
                    ],
                )
                self.assertGetResponse(
                    'cae_tools:api_semester',
                    data={'identifier': str(semester.name).lower()},
                    expected_content=[
                        '"name": "' + str(semester.name) + '",',
                        '"start_date": "' + str(semester.start_date) + '",',
                        '"end_date": "' + str(semester.end_date) + '"',
                    ],
                )
                # Check querying by dates.
                self.assertGetResponse(
                    'cae_tools:api_semester',
                    data={
                        'start_date': str(semester.start_date),
                        'end_date': str(semester.end_date),
                    },
                    expected_content=[
                        '"name": "' + str(semester.name) + '",',
                        '"start_date": "' + str(semester.start_date) + '",',
                        '"end_date": "' + str(semester.end_date) + '"',
                    ],
                )
