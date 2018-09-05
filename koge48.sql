-- phpMyAdmin SQL Dump
-- version 4.8.3
-- https://www.phpmyadmin.net/
--
-- 主机： localhost
-- 生成日期： 2018-09-05 14:23:42
-- 服务器版本： 5.5.61
-- PHP 版本： 7.2.8

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- 数据库： `koge48`
--
CREATE DATABASE IF NOT EXISTS `koge48` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `koge48`;

-- --------------------------------------------------------

--
-- 表的结构 `apikey`
--

DROP TABLE IF EXISTS `apikey`;
CREATE TABLE `apikey` (
  `uid` int(11) NOT NULL,
  `apikey` varchar(64) CHARACTER SET latin1 NOT NULL,
  `apisecret` varchar(64) CHARACTER SET latin1 NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- 表的结构 `balance`
--

DROP TABLE IF EXISTS `balance`;
CREATE TABLE `balance` (
  `uid` int(11) NOT NULL,
  `bal` double NOT NULL DEFAULT '0',
  `ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- 表的结构 `changelog`
--

DROP TABLE IF EXISTS `changelog`;
CREATE TABLE `changelog` (
  `height` bigint(20) UNSIGNED NOT NULL,
  `uid` int(11) NOT NULL,
  `differ` double NOT NULL COMMENT 'how many coins are changed',
  `ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `memo` text CHARACTER SET latin1 NOT NULL COMMENT 'how many digs during this block'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- 触发器 `changelog`
--
DROP TRIGGER IF EXISTS `autobalance`;
DELIMITER $$
CREATE TRIGGER `autobalance` AFTER INSERT ON `changelog` FOR EACH ROW INSERT INTO balance (uid,bal) VALUES (new.uid,new.differ) ON DUPLICATE KEY UPDATE balance.bal=balance.bal+new.differ
$$
DELIMITER ;

--
-- 转储表的索引
--

--
-- 表的索引 `apikey`
--
ALTER TABLE `apikey`
  ADD PRIMARY KEY (`uid`);

--
-- 表的索引 `balance`
--
ALTER TABLE `balance`
  ADD PRIMARY KEY (`uid`);

--
-- 表的索引 `changelog`
--
ALTER TABLE `changelog`
  ADD PRIMARY KEY (`height`),
  ADD UNIQUE KEY `id` (`height`);

--
-- 在导出的表使用AUTO_INCREMENT
--

--
-- 使用表AUTO_INCREMENT `changelog`
--
ALTER TABLE `changelog`
  MODIFY `height` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
