
local DISCOUNT_PERCENT = 10
local MIN_TOTAL = 300000 -- 3000 рублей

function calculate(cart)
    local subtotal = 0
    for _, item in ipairs(cart) do
        subtotal = subtotal + item.price * item.quantity
    end

    local discount = 0
    if subtotal >= MIN_TOTAL then
        discount = math.floor(subtotal * DISCOUNT_PERCENT / 100 + 0.5)
    end
    return {
        discount = discount,
        message = "Скидка " .. DISCOUNT_PERCENT .. "% от 3000 рублей"
    }
end
