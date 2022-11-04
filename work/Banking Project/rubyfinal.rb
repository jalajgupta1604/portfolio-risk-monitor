# options show on screen-------------------
puts "Select option accordingly:"
puts "Press 1 for Account Opening Form"
puts "Press 2 for Customers Details"
puts "Press 3 for Amount Transaction"
puts "Press 4 for Passbook"
puts "Press 5 for Exit"

# class creation-------------
class BankingProject

  $users_array = []         # Global variable array
  @@user_count = 0          # class variable

  def self.cust_data()
    @@user_count = @@user_count + 1

    print "Enter your name:"
    name = gets.chomp.to_s

    print "Enter your Balance Amount:"
    balance = gets.chomp.to_i
   
    print "Enter your password:"
    pwd = gets.chomp.to_i
    if pwd.size ==3
      else 
        puts "Error: max limit is 3"
        puts "Enter your correct password"
        pwd = gets.chomp.to_i
    end
    p "Form Complete"

    @user_data = {id: @@user_count, name: name, balance: balance, pwd: pwd, transactions: []}
    $users_array.push(@user_data)
  end
  # Customer list method------------
  def self.cust_details()   
    puts $users_array
  end

  # Transaction between 2 users-----------------------------
  def self.amount_transaction(sender,receiver,amount)
    user1 = $users_array.find{ |x| x[:id] == sender}
    user2 = $users_array.find{ |x| x[:id] == receiver}

    debit = user1[:balance] - amount
    user1[:balance] = debit
    transaction2 = {sender: sender, receiver: receiver, amount: -amount} # amount debited from sender
    user1[:transactions].push(transaction2)

    credit = user2[:balance] + amount
    user2[:balance] = credit
    transaction2 = {sender: sender, receiver: receiver, amount: amount} # amount credited to receiver
    user2[:transactions].push(transaction2)

    return user1[:balance], user2[:balance] # call user1 and user2 account in passbook
  end

    # comparing/finding id's for transactions------------
  def self.sender_cust(sender)
    $users_array.find{ |x| x[:id]==sender}
  end
  def self.receiver_cust(receiver)
    $users_array.find{|y| y[:id]==receiver}
  end
  def self.sender_balance(sender,amount)
    user= $users_array.find{|z| z[:id]==sender}
    if amount<=user[:balance]
      user[:balance] = user[:balance] - amount
    else
      error
    end
  end
  def self.validate_pin(sender,pin)
    user=$users_array.find{|a| a[:id]==sender}
    pin=user[:pwd]
  end

  # Amount Transaction conditions------------------
  def self.transfer_process()

    puts "Enter sender's ID"
    sender= gets.chomp.to_i
    puts "Enter receiver's ID"
    receiver= gets.chomp.to_i
    puts "Enter Amount"
    amount= gets.chomp.to_i
    puts "Enter sender's PIN"
    pwd= gets.chomp.to_i

    @transfer_data={sender:sender, receiver:receiver, amount:amount, pwd:pwd}
    amount_transaction(sender,receiver,amount)    # Call amount transaction method for add & deduct amount
  end
  # Passbook method-------------------------
=begin
  def self.passbook()
    puts "Enter Customer ID:"
    customerID=gets.chomp.to_i
    user = $users_array.find{|x| x[:id] == customerID}
    user[:transactions]
  end
=end
  def self.cust_passbook(custID)
    user = $users_array.find{ |x| x[:id] == custID}
    user[:transactions]
  end
  def self.show_passbook()
      print "Enter user-id: "
      custID = gets.chomp.to_i
      if $users_array.find{ |x| x[:id] == custID} != nil
        p cust_passbook(custID)
      else
        puts "Unknown User Id"
      end
    end


  loop do
    case gets.chomp.to_i
      when 1
        puts "Kindly fill your details"
        cust_data
      when 2
        puts "Customer List"
        cust_details
      when 3
        puts "Amount Transaction"
        transfer_process
      when 4
        puts "Passbook"
        show_passbook()
      when 5
        puts "Thank you for Banking with us"
        break
    end
  end
end

