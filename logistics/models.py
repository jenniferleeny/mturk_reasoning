'''
Copyright (c) 2014, Igor Labutov
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those
of the authors and should not be interpreted as representing official policies,
either expressed or implied, of the FreeBSD Project.
'''

from django.db import models
from django.contrib import admin
import json
import re
import random
from Mturk import Mturk

class Feedback(models.Model):
	feedback      = models.TextField(default='')

	def __unicode__(self):
		return u'%s' % (self.feedback)


class Turker(models.Model):
	worker_id             = models.CharField(max_length=100, primary_key=True)
	level                 = models.IntegerField(default=0)
	pending_assignments   = models.TextField(default='[]')
	paid_assignments      = models.TextField(default='[]')
	bonus_assignments     = models.TextField(default='{}')


	class PaymentError(Exception):
		pass

	class MsgError(Exception):
		pass

	def complete_assignment(self, assignmentId):
		pending_assignments = json.loads(self.pending_assignments)
		pending_assignments.append(assignmentId)
		self.pending_assignments = json.dumps(pending_assignments)
		self.save()

	def pay_for_assignment(self, assignmentId, mturk=Mturk()):
		try:
			mturk.approve_assignment(assignmentId)	
			pending_assignments      = json.loads(self.pending_assignments)
			paid_assignments         = json.loads(self.paid_assignments)
			pending_assignments.remove(assignmentId)
			paid_assignments.append(assignmentId)	
			self.pending_assignments = json.dumps(pending_assignments)
			self.paid_assignments    = json.dumps(paid_assignments)
			self.save()
		except Mturk.MturkException, msg:
			raise self.PaymentError('\033[91m [failed] \033[0m')


		
	def pay_for_all_assignments(self, mturk=Mturk()):
		pending_assignments = json.loads(self.pending_assignments)
		for assignment in pending_assignments:
			try:
				print '\033[93mtrying to pay %s for %s\033[0m' % (self.worker_id, assignment)
				self.pay_for_assignment(assignment, mturk)
				print '\033[92m [success]\033[0m'
			except self.PaymentError, msg:
				print msg

	def send_message(self, subject, body, mturk=Mturk()):
		#mturk.send_message(self.worker_id, subject, body)	
		try:
			print '\033[93mtrying to send MSG to %s for' % (self.worker_id)
			mturk.send_message(self.worker_id, subject, body)	
			print '\033[92m [success]\033[0m'
		except Mturk.MturkException:
			raise self.MsgError('\033[91m [failed]\033[0m')


	def grant_bonus(self, assignmentId, amount, message, mturk=Mturk()):
		try:
			print '\033[93mtrying to grant BONUS to %s for %s\033[0m' % (self.worker_id, assignmentId)
			bonus_assignments           = json.loads(self.bonus_assignments)
			mturk.grant_bonus(self.worker_id, assignmentId, amount, message)	
			bonus_assignments[assignmentId] = amount
			self.bonus_assignments      = json.dumps(bonus_assignments)
			print '\033[92m [success]\033[0m'
		except Mturk.MturkException:
			raise self.PaymentError('\033[91m [failed]\033[0m')

	def __unicode__(self):
		return u'%s' % (self.worker_id)
