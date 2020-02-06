DROP TABLE IF EXISTS auc_hist;
CREATE TABLE auc_hist (
	itemId INT NOT NULL,
	marketValue INT,
	minBuyout INT,
	historical INT,
	numAuctions INT,
	scanTime TIMESTAMP NOT NULL,
	PRIMARY KEY (itemId, scanTime)
)
;