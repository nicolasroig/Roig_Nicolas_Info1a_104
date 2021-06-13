-- OM 2021.02.17
-- FICHIER MYSQL POUR FAIRE FONCTIONNER LES EXEMPLES
-- DE REQUETES MYSQL
-- Database: roig_nicolas_info_1a

-- Détection si une autre base de donnée du même nom existe

DROP DATABASE IF EXISTS roig_nicolas_info_1a;

-- Création d'un nouvelle base de donnée

CREATE DATABASE IF NOT EXISTS roig_nicolas_info_1a;

-- Utilisation de cette base de donnée

USE roig_nicolas_info_1a;
-- --------------------------------------------------------

CREATE TABLE `t_client` (
  `Id_client` int(11) NOT NULL,
  `nom` varchar(30) NOT NULL,
  `prenom` varchar(30) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Contenu de la table `t_client`
--

INSERT INTO `t_client` (`Id_client`, `nom`, `prenom`) VALUES
(1, 'Wick', 'John'),
(2, 'christian', 'stophe'),
(3, 'christian', 'John'),
(4, 'benteke', 'ronaldo'),
(5, 'eden', 'hazard'),
(6, 'philipp', 'coutinho'),
(7, 'luis', 'suarez');

-- --------------------------------------------------------

--
-- Structure de la table `t_materiel`
--

CREATE TABLE `t_materiel` (
  `Id_materiel` int(11) NOT NULL,
  `materiel` tinytext NOT NULL,
  `numero_de_serie` tinytext NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Contenu de la table `t_materiel`
--

INSERT INTO `t_materiel` (`Id_materiel`, `materiel`, `numero_de_serie`) VALUES
(1, 'ecran', '45645356r'),
(2, 'souris', '34645t'),
(3, 'clavier', '435654r'),
(4, 'clavier', '122123'),
(5, 'pc portable', '3245024780620');

-- --------------------------------------------------------

--
-- Structure de la table `t_preter_materiel`
--

CREATE TABLE `t_preter_materiel` (
  `Id_preter_materiel` int(11) NOT NULL,
  `Etat_avant_pret` text NOT NULL,
  `date_pret` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `fk_materiel` int(11) NOT NULL,
  `fk_client` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Contenu de la table `t_preter_materiel`
--

INSERT INTO `t_preter_materiel` (`Id_preter_materiel`, `Etat_avant_pret`, `date_pret`, `fk_materiel`, `fk_client`) VALUES
(1, 'nickel', '2021-03-04 21:38:41', 1, 1),
(2, 'tres propre', '2021-03-04 21:38:52', 2, 2),
(3, 'une legere tache', '2021-03-04 21:39:13', 3, 3),
(4, 'propre comme un sous neuf', '2021-03-04 21:39:33', 4, 4),
(5, 'le matos pue un peu', '2021-03-04 21:39:49', 5, 5);

-- --------------------------------------------------------

--
-- Structure de la table `t_retour_materiel`
--

CREATE TABLE `t_retour_materiel` (
  `Id_retour_materiel` int(11) NOT NULL,
  `date_retour` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `etat_apres` text NOT NULL,
  `fk_materiel` int(11) NOT NULL,
  `fk_client` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Contenu de la table `t_retour_materiel`
--

INSERT INTO `t_retour_materiel` (`Id_retour_materiel`, `date_retour`, `etat_apres`, `fk_materiel`, `fk_client`) VALUES
(3, '2021-03-01 21:20:21', 'Yo', 1, 1),
(4, '2021-03-01 21:20:21', 'yo', 1, 1);

-- --------------------------------------------------------

--
-- Structure de la table `t_technicien`
--

CREATE TABLE `t_technicien` (
  `Id_technicien` int(11) NOT NULL,
  `technicien` varchar(3) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Index pour les tables exportées
--

--
-- Index pour la table `t_client`
--
ALTER TABLE `t_client`
  ADD PRIMARY KEY (`Id_client`);

--
-- Index pour la table `t_materiel`
--
ALTER TABLE `t_materiel`
  ADD PRIMARY KEY (`Id_materiel`);

--
-- Index pour la table `t_preter_materiel`
--
ALTER TABLE `t_preter_materiel`
  ADD PRIMARY KEY (`Id_preter_materiel`),
  ADD KEY `fk_materiel` (`fk_materiel`),
  ADD KEY `fk_client` (`fk_client`);

--
-- Index pour la table `t_retour_materiel`
--
ALTER TABLE `t_retour_materiel`
  ADD PRIMARY KEY (`Id_retour_materiel`),
  ADD KEY `fk_materiel` (`fk_materiel`),
  ADD KEY `fk_client` (`fk_client`);

--
-- Index pour la table `t_technicien`
--
ALTER TABLE `t_technicien`
  ADD PRIMARY KEY (`Id_technicien`);

--
-- AUTO_INCREMENT pour les tables exportées
--

--
-- AUTO_INCREMENT pour la table `t_client`
--
ALTER TABLE `t_client`
  MODIFY `Id_client` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;
--
-- AUTO_INCREMENT pour la table `t_materiel`
--
ALTER TABLE `t_materiel`
  MODIFY `Id_materiel` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;
--
-- AUTO_INCREMENT pour la table `t_preter_materiel`
--
ALTER TABLE `t_preter_materiel`
  MODIFY `Id_preter_materiel` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;
--
-- AUTO_INCREMENT pour la table `t_retour_materiel`
--
ALTER TABLE `t_retour_materiel`
  MODIFY `Id_retour_materiel` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;
--
-- AUTO_INCREMENT pour la table `t_technicien`
--
ALTER TABLE `t_technicien`
  MODIFY `Id_technicien` int(11) NOT NULL AUTO_INCREMENT;
--
-- Contraintes pour les tables exportées
--

--
-- Contraintes pour la table `t_preter_materiel`
--
ALTER TABLE `t_preter_materiel`
  ADD CONSTRAINT `t_preter_materiel_ibfk_1` FOREIGN KEY (`fk_materiel`) REFERENCES `t_materiel` (`Id_materiel`),
  ADD CONSTRAINT `t_preter_materiel_ibfk_2` FOREIGN KEY (`fk_client`) REFERENCES `t_client` (`Id_client`);

--
-- Contraintes pour la table `t_retour_materiel`
--
ALTER TABLE `t_retour_materiel`
  ADD CONSTRAINT `t_retour_materiel_ibfk_1` FOREIGN KEY (`fk_materiel`) REFERENCES `t_materiel` (`Id_materiel`),
  ADD CONSTRAINT `t_retour_materiel_ibfk_2` FOREIGN KEY (`fk_client`) REFERENCES `t_client` (`Id_client`);
