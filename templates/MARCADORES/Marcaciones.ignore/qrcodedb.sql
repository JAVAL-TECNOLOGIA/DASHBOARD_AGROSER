-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1:3307
-- Tiempo de generación: 07-11-2023 a las 22:09:55
-- Versión del servidor: 10.4.25-MariaDB
-- Versión de PHP: 7.4.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `qrcodedb`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `attendance`
--

CREATE TABLE `attendance` (
  `ID` int(11) NOT NULL,
  `STUDENTID` varchar(250) NOT NULL,
  `TIMEIN` time NOT NULL,
  `TIMEOUT` time DEFAULT NULL,
  `LOGDATE` date NOT NULL,
  `STATUS` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `schedules`
--

CREATE TABLE `schedules` (
  `ID` int(11) NOT NULL,
  `TIMEIN` time NOT NULL,
  `TIMEOUT` time NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Volcado de datos para la tabla `schedules`
--

INSERT INTO `schedules` (`ID`, `TIMEIN`, `TIMEOUT`) VALUES
(1, '07:00:00', '16:00:00'),
(2, '08:00:00', '17:00:00'),
(3, '09:00:00', '18:00:00'),
(4, '10:00:00', '19:00:00');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `student`
--

CREATE TABLE `student` (
  `ID` int(11) NOT NULL,
  `STUDENTID` varchar(250) NOT NULL,
  `FIRSTNAME` varchar(250) NOT NULL,
  `MNAME` varchar(250) NOT NULL,
  `LASTNAME` varchar(250) NOT NULL,
  `AGE` int(11) NOT NULL,
  `GENDER` varchar(250) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `attendance`
--
ALTER TABLE `attendance`
  ADD PRIMARY KEY (`ID`);

--
-- Indices de la tabla `schedules`
--
ALTER TABLE `schedules`
  ADD PRIMARY KEY (`ID`);

--
-- Indices de la tabla `student`
--
ALTER TABLE `student`
  ADD PRIMARY KEY (`ID`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `attendance`
--
ALTER TABLE `attendance`
  MODIFY `ID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=213;

--
-- AUTO_INCREMENT de la tabla `schedules`
--
ALTER TABLE `schedules`
  MODIFY `ID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `student`
--
ALTER TABLE `student`
  MODIFY `ID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2236;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
