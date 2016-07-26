#
# Cookbook Name:: MiniProject
# Recipe:: default
#
# Copyright (c) 2016 The Authors, All Rights Reserved.
sudo yum -y install httpd
sudo service httpd start

#template '/var/www/html/index.html' do
#  source 'index.html.erb'
#end
file '/var/www/html/index.html' do
  content '<html>
  <body>
    <h1>Automation for the People/h1>
  </body>
</html>'
end
