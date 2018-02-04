1) Platform:

	Operating System: Windows 10
	Distalgo version: 1.0.9
	Python Implementation: CPython
	Python version: 3.6
	Types of hosts:
		For single host: Windows operating system laptop(without any VMs)
		For Multiple hosts: One laptop with Windows operating system(without any VMs) and another laptop with windows operating system(without any VMs).

2) Instructions:

	In order to run the project files first we need to install the following python libraries.
		1) DistAlgo : Run the following command to install distalgo in your machine
			cmd : pip install pyDistAlgo

		2) NACL : A python library for encryption and digital signatures. Run the follwing command to install this library
		    cmd : pip install pynacl

	For a single host(Windows machne without VMs):
		1) Open the command prompt and navigate into the folder where the files of the project are present.
			cmd: cd path_to_the_project_folder/project_folder_name

		2) Command to compile and run the main file on a single node for all the processes.
			cmd: python -m da main.da path_to_configuration_file/configuration_file_name.txt
	
		   Note: For larger Psudorandom requests we need to mention the buffer size, so the above commands become,
			python -m da --message-buffer-size size_in_bytes main.da path_to_configuration_file/configuration_file_name.txt

		3) Command to compile and run the different processes on different nodes. 
			a) Replace this code in the main.da file
				c = list(new(Client.CL, num= num_client))
				r = list(new(Replica.replica , num =num_replica))
				olympus = list(new(Olympus.Olympus,num=1))
			
			   with this code
				c = list(new(Client.CL, num= num_client,at='ClientNode'))
				r = list(new(Replica.replica , num =num_replica,at='ReplicaNode'))
				olympus = list(new(Olympus.Olympus,num=1,at='OlympusNode'))

			b) Open three different command prompts and in all the three navigate into the project directory and then type the follwing commands:
				python -m da -n OlympusNode main.da path_to_configuration_file/configuration_file_name.txt ---- type this command in the first command prompt
				python -m da -n ClientNode main.da path_to_configuration_file/configuration_file_name.txt ---- type this command in the second command prompt
				python -m da -n ReplicaNode main.da path_to_configuration_file/configuration_file_name.txt --- type this command in the third commnad prompt 

			   Note: For larger Psudorandom requests we need to mention the buffer size, so the above commands become,
				python -m da -n OlympusNode --message-buffer-size size_in_bytes main.da path_to_configuration_file/configuration_file_name.txt ---- type this command in the first command prompt
				python -m da -n ClientNode --message-buffer-size size_in_bytes main.da path_to_configuration_file/configuration_file_name.txt ---- type this command in the second command prompt
				python -m da -n ReplicaNode --message-buffer-size size_in_bytes main.da path_to_configuration_file/configuration_file_name.txt --- type this command in the third commnad prompt 


	For multiple hosts(Windows machines without VMs):
		1) In one machine open two command prompts and in the another machine open one command prompt.

		2) Navigate into the folder where the files of the project are present in all the command prompts.
			cmd: cd path_to_the_project_folder/project_folder_name

		3) In the machine with only one command prompt type the following command
			cmd: python -m da -H ip_address_of_the_current_machine -n OlympusNode main.da path_to_configuration_file/configuration_file_name.txt

		4) In the other machine in one of the command prompts type the follwing command
			cmd: python -m da -H ip_address_of_the_current_machine -R ip_address_of_the_machine_rumming_OlympusNode -n ClientNode -D main.da path_to_configuration_file/configuration_file_name.txt

		   and in the other command prompt type the following command
			cmd: python -m da -H ip_address_of_the_current_machine -R ip_address_of_the_machine_rumming_OlympusNode -n ReplicaNode -D main.da path_to_configuration_file/configuration_file_name.txt

3) Workload Generation:

	pseudocode:

	//prw is the list of operations from which an operation will be picked randomly
	x = []   //Empty list to store the generated random requests
	//iterate over the number of requests and append the randomly picked operation into the list x
	for i in xrange(no_of_requests):
		x.append(prw[(seed+i)%len(prw)]) // (seed+i)%len(prw) this logic ensures that for the same seed same psudorandom requests are generated.

4) Bugs:
	a) When the buffer size given as an input is larger than required then the machine gets struck
	b) Log messages get trucated sometimes when there are a large number of concurrent processes running 

   Limitations:
	a) Sometimes the result check fails at the Parent module for large number of pseudorandom requests
 

5) Contributions:

	a) Team Member 1:
		- Code for the Replica Module.
		- Multihost-execution.

	b) Team Member 2:
		- Code for Client Module.
		- Code for Parent Module.
		- Code for Olympus Module
		- Documentation.
		- Code for parsing the configuration file.
		- Documented Log files.

6) Main Files:

	First navigate into the src folder
	
	main.da is the main file name that is to be given as the input to the command line.
	Olympus.da is the module for the Olympus process and it has been imported into the main file.
	Client.da is the module for the Client process and it has been imported into the main file.
	Replica.da is the module for the Replica process and it has been imported into the main file.
	Parent.da is the module for result verification from different clients.

7) Code Size:
	
	1a) Algorithm:
		main.da : 33 non-blank and non-commented LOC
		Olympus.da : 255 non-blank and non-commented LOC
		Client.da : 135 non-blank and non-commented LOC
		Replica.da : 1180 non-blank and non-commented LOC
		Parent.da : 56 non-blank and non-commented LOC

	    Other:
		Configuration files:
			a) Failure_free_config: 8 non-blank and non-commented LOC
			b) Client_request_fail_config: 12 non-blank and non-commented LOC
			c) Forwarded_request_config: 9 non-blank and non-commented LOC
			d) Result_shuttle_config: 12 non-blank and non-commented LOC
			e) Shuttle_failure_config: 11 non-blank and non-commented LOC
			f) Stress_test_config: 17 non-blank and non-commented LOC
			g) Catchup_drop_invalid_order_sig: 10 non-blank and non-commented LOC
			h) Checkpoint_change_oper: 10 non-blank and non-commented LOC
			i) Client_request_change_result: 10 non-blank and non-commented LOC
			j) Client_request_increment_slot: 10 non-blank and non-commented LOC
			k) Completed_checkpoint_drop_chkstmt: 10 non-blank and non-commented LOC
			l) Forwarded_request_drop_result_stmt: 10 non-blank and non-commented LOC
			m) Get_running_state_extra_op: 10 non-blank and non-commented LOC
			n) Result_shuttle_drop: 11 non-blank and non-commented LOC
			o) Shuttle_inv_resultsig_newconf_drop: 11 non-blank and non-commented LOC
			p) Wedge_req_truncate_hist: 10 non-blank and non-commented LOC
			q) Wedge_request_crash: 10 non-blank and non-commented LOC
			r) Perform_900: 10 non-blank and non-commented LOC

		Testing.txt:
			350 non-blank and non-commented LOC

	1b) We use CLOC https://github.com/AlDanial/cloc to find out the lines of code.
	    For windows machines download the available binaries from the above mentioned github link and then navigate to the folder where the .exe file has been downloaded from the command prompt
	    To count the number of lines in each module:
	    cmd: cloc-1.74.exe module_name.da
	    To count the total number of lines in the entire project:
	    cmd: cloc-1.74.exe project_folder_name

	2) 1659 LOC for Algorithm and 540 LOC for failure_injection, logging, debugging etc.

8) Language Feature Usage:

	List Comprehensions: 13
	Dictionary Comprehensions: 22
	Set Comprehensions: 0
	Aggregations: 0
	Quantification: 0