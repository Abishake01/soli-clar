;; Example of what the converted Clarity code might look like
;; This is a simplified example and not a complete implementation

;; Define NFT constants
(define-constant contract-owner tx-sender)
(define-constant err-owner-only (err u100))
(define-constant err-not-found (err u101))
(define-constant err-max-supply-reached (err u102))
(define-constant err-insufficient-payment (err u103))

;; Define NFT data variables
(define-data-var token-id-nonce uint u0)
(define-data-var base-token-uri (string-utf8 256) "")
(define-data-var mint-price uint u50000000) ;; 0.05 STX in micro-STX
(define-data-var total-supply uint u0)
(define-constant max-supply u10000)

;; NFT token storage
(define-non-fungible-token my-nft uint)

;; Map for token URI storage
(define-map token-uris uint (string-utf8 256))

;; Map for token ownership
(define-map token-owner uint principal)

;; Check if caller is the contract owner
(define-private (is-contract-owner)
  (is-eq tx-sender contract-owner))

;; Get the last token ID
(define-read-only (get-last-token-id)
  (var-get token-id-nonce))

;; Get the total supply
(define-read-only (get-total-supply)
  (var-get total-supply))

;; Get the owner of a token
(define-read-only (get-owner (token-id uint))
  (map-get? token-owner token-id))

;; Get the token URI
(define-read-only (get-token-uri (token-id uint))
  (map-get? token-uris token-id))

;; Mint a new NFT
(define-public (mint-nft (recipient principal) (token-uri (string-utf8 256)))
  (let
    (
      (current-supply (var-get total-supply))
      (new-id (+ (var-get token-id-nonce) u1))
    )
    
    ;; Check supply limit
    (asserts! (< current-supply max-supply) err-max-supply-reached)
    
    ;; Check payment
    (asserts! (>= (stx-get-balance tx-sender) (var-get mint-price)) err-insufficient-payment)
    
    ;; Transfer STX
    (try! (stx-transfer? (var-get mint-price) tx-sender contract-owner))
    
    ;; Mint NFT
    (try! (nft-mint? my-nft new-id recipient))
    
    ;; Store token URI
    (map-set token-uris new-id token-uri)
    
    ;; Store token owner
    (map-set token-owner new-id recipient)
    
    ;; Update counters
    (var-set token-id-nonce new-id)
    (var-set total-supply (+ current-supply u1))
    
    (ok new-id)
  )
)

;; Set mint price - owner only
(define-public (set-mint-price (new-price uint))
  (begin
    (asserts! (is-contract-owner) err-owner-only)
    (var-set mint-price new-price)
    (ok true)
  )
)

;; Set base URI - owner only
(define-public (set-base-uri (new-base-uri (string-utf8 256)))
  (begin
    (asserts! (is-contract-owner) err-owner-only)
    (var-set base-token-uri new-base-uri)
    (ok true)
  )
)

;; Withdraw balance - owner only
(define-public (withdraw)
  (let
    (
      (balance (stx-get-balance (as-contract tx-sender)))
    )
    (begin
      (asserts! (is-contract-owner) err-owner-only)
      (asserts! (> balance u0) (err u104))
      (as-contract (stx-transfer? balance tx-sender contract-owner))
    )
  )
)
