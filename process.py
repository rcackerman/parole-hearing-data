import sqlite3

conn = sqlite3.connect('parolees.db')

c = conn.cursor()
c.execute('''create table parolees 
          (nysid, din, sex, birth_date, race_ethnicity,
          	housing_or_interview_facility, parole_board_interview_date,
          	parole_board_interview type, interview_decision, year_of_entry,
          	aggregated_minimum_sentence, aggregated_maximum_sentence, release_date,
          	release_type, housing_release_facility, parole_eligibility_date, conditional_release_date,
          	maximum_expiration_date, parole_max_exp_date, post_release_supervision_max_exp_date,
						parole_board_discharge_date);
''')

conn.commit()
# #And now we clean
# for parolee in parolees:
#   parolee = parolee[1:len(parolee)]
