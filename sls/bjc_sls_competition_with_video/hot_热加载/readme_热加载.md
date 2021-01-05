 java -jar maven-demo1230-0.0.1-SNAPSHOT.war –httpPort=端口


如果需要使用该功能，需要将
src\main\java\下的 org 包、
src\main\resources\下的 mybatis-refresh.properties 文件、
src\main\resources\下的 ApplicationContext-dao.xml 文件
拖到自己的项目下，mybatis的mapper xml文件放到src\main\resources\mappings\下即可。之后启动项目之后， 修改mapper.xml中的SQL语句之后，build下即可，不需要再重启项目
