-- phpMyAdmin SQL Dump
-- version 4.8.3
-- https://www.phpmyadmin.net/
--
-- Host: localhost
-- Generation Time: Dec 30, 2018 at 08:30 AM
-- Server version: 5.5.62
-- PHP Version: 7.2.11

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `koge48`
--

-- --------------------------------------------------------

--
-- Table structure for table `apikey`
--

CREATE TABLE `apikey` (
  `uid` int(11) NOT NULL,
  `apikey` varchar(64) CHARACTER SET latin1 NOT NULL,
  `apisecret` varchar(64) CHARACTER SET latin1 NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='Used to keep user''s apikey/secret from binance';

-- --------------------------------------------------------

--
-- Table structure for table `balance`
--

CREATE TABLE `balance` (
  `uid` int(11) NOT NULL,
  `full_name` text NOT NULL,
  `bal` double NOT NULL DEFAULT '0',
  `ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='the balance of koge, derived from changelog.';

-- --------------------------------------------------------

--
-- Table structure for table `bnb`
--

CREATE TABLE `bnb` (
  `uid` int(11) NOT NULL,
  `onchain` double NOT NULL DEFAULT '0',
  `offchain` double NOT NULL DEFAULT '0',
  `ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='regularly updated with user''s bnb balance, for airdrop';

-- --------------------------------------------------------

--
-- Table structure for table `changelog`
--

CREATE TABLE `changelog` (
  `height` bigint(20) UNSIGNED NOT NULL,
  `uid` int(11) NOT NULL,
  `differ` double NOT NULL COMMENT 'how many coins are changed',
  `ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `memo` text CHARACTER SET latin1 NOT NULL COMMENT 'how many digs during this block',
  `source` varchar(32) NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='how koge is + or -';

--
-- Triggers `changelog`
--
DELIMITER $$
CREATE TRIGGER `autobalance_delete` AFTER DELETE ON `changelog` FOR EACH ROW update balance set balance.bal = balance.bal - old.differ where balance.uid = old.uid
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `autobalance_insert` AFTER INSERT ON `changelog` FOR EACH ROW INSERT INTO balance (uid,bal) VALUES (new.uid,new.differ) ON DUPLICATE KEY UPDATE balance.bal=balance.bal+new.differ
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `cheque`
--

CREATE TABLE `cheque` (
  `number` double NOT NULL,
  `sid` int(11) NOT NULL,
  `did` int(11) NOT NULL DEFAULT '0',
  `ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `code` varchar(32) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `eth`
--

CREATE TABLE `eth` (
  `uid` int(11) NOT NULL,
  `eth` varchar(42) NOT NULL,
  `ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='used to keep user''s eth address of bnb';

--
-- Indexes for dumped tables
--

--
-- Indexes for table `apikey`
--
ALTER TABLE `apikey`
  ADD PRIMARY KEY (`uid`),
  ADD UNIQUE KEY `apikey` (`apikey`);

--
-- Indexes for table `balance`
--
ALTER TABLE `balance`
  ADD PRIMARY KEY (`uid`);

--
-- Indexes for table `bnb`
--
ALTER TABLE `bnb`
  ADD PRIMARY KEY (`uid`);

--
-- Indexes for table `changelog`
--
ALTER TABLE `changelog`
  ADD PRIMARY KEY (`height`),
  ADD UNIQUE KEY `id` (`height`);

--
-- Indexes for table `cheque`
--
ALTER TABLE `cheque`
  ADD UNIQUE KEY `code` (`code`);

--
-- Indexes for table `eth`
--
ALTER TABLE `eth`
  ADD PRIMARY KEY (`uid`),
  ADD UNIQUE KEY `eth` (`eth`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `changelog`
--
ALTER TABLE `changelog`
  MODIFY `height` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
