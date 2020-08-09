#!/usr/bin/python
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
import time                                                                                          
import hmac
import sha
import base64
import urllib
import urllib2
import pprint
import re

class Mturk(object):
	def __init__(self, access_key='AKIAIPLNX4562EHF2LXQ', secret_access_key='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'):
		self.AWS_ACCESS_KEY_ID      = access_key
		self.AWS_SECRET_ACCESS_KEY  = secret_access_key
		#self.SERVICE_VERSION        = '2012-03-25'
		self.SERVICE_VERSION        = '2014-08-15'
		self.BASE_URL               = "https://mechanicalturk.amazonaws.com/?Service=AWSMechanicalTurkRequester"

	class MturkException(Exception):
		pass

	def _generate_timestamp(self, gmtime):
	    return time.strftime("%Y-%m-%dT%H:%M:%SZ", gmtime)

	def _generate_signature(self, service, operation, timestamp, secret_access_key):
	    my_sha_hmac = hmac.new(secret_access_key, service + operation + timestamp, sha)
	    my_b64_hmac_digest = base64.encodestring(my_sha_hmac.digest()).strip()
	    return my_b64_hmac_digest

	def _generate_timestamp_and_signature(self, operation):
		timestamp = self._generate_timestamp(time.gmtime())
	        signature = self._generate_signature('AWSMechanicalTurkRequester', operation, timestamp, self.AWS_SECRET_ACCESS_KEY) 
		return timestamp, signature
		

	def _REST_request(self, params):
		request_url = self.BASE_URL + '&' + urllib.urlencode(params)
		response = urllib2.urlopen(request_url).read()
		if re.findall('Failure|Error', response):
			raise self.MturkException(response)
		

	def approve_assignment(self, assignment_id):
		operation = 'ApproveAssignment'
		timestamp, signature = self._generate_timestamp_and_signature(operation)

		params = { "AWSAccessKeyId" :  self.AWS_ACCESS_KEY_ID,
			   "Version"        :  self.SERVICE_VERSION,
			   "Operation"      :  operation,
		           "Signature"      :  signature,
			   "Timestamp"      :  timestamp,
			   "AssignmentId"   :  assignment_id,
		         }

		self._REST_request(params)

	def grant_bonus(self, worker_id, assignment_id, amount, message):
		operation = 'GrantBonus'
		timestamp, signature = self._generate_timestamp_and_signature(operation)

		params = {"AWSAccessKeyId"              :  self.AWS_ACCESS_KEY_ID,
			  "Version"                     :  self.SERVICE_VERSION,
			  "Operation"                   :  operation,
			  "Signature"                   :  signature,
			  "Timestamp"                   :  timestamp,
			  "AssignmentId"                :  assignment_id,
			  "WorkerId.1"                  :  worker_id,
			  "BonusAmount.1.Amount"        :  str(amount),
			  "BonusAmount.1.CurrencyCode"  : "USD",
			  "Reason"                      :  message
		          }

		self._REST_request(params)

	def send_message(self, worker_id, subject, body):
		operation = 'NotifyWorkers'
		timestamp, signature = self._generate_timestamp_and_signature(operation)
		print timestamp, signature

		params = {"AWSAccessKeyId" : self.AWS_ACCESS_KEY_ID,
			  "Version"        : self.SERVICE_VERSION,
			  "Operation"      : operation,
			  "Signature"      : signature,
			  "Timestamp"      : timestamp,
			  "Subject"        : subject,
			  "MessageText"    : body,
			  "WorkerId.1"     : worker_id,
	           	 }

		self._REST_request(params)
